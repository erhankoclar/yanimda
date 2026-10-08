from unittest.mock import patch

from django.db import connection
from django.test.utils import CaptureQueriesContext
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework.throttling import SimpleRateThrottle

from apps.care.factories import ServiceInquiryFactory
from apps.care.models import CareRequest
from apps.care.tests.factories import care_request_data, make_care_request, make_service, make_user
from apps.care.throttles import CareRequestCreateRateThrottle


def make_bilingual_service():
    """
    Türkçe ve İngilizce çevirisi olan hizmet oluşturur.

    Returns:
        ServiceType: İki dilde adı olan hizmet.
    """
    service = make_service()
    service.set_current_language('en')
    service.name = f'Service {service.pk}'
    service.description = 'Description'
    service.save()
    return service


class CareNPlusOneTests(APITestCase):
    """Bakım uç noktalarının ilişkili kayıt sayısından bağımsız sorgu sayısıyla çalıştığını doğrular."""

    LANGUAGES = ({}, {'HTTP_ACCEPT_LANGUAGE': 'en'})

    def measure(self, method, url, data=None, **extra):
        """
        Tek bir isteğin çalıştırdığı SQL sorgusu sayısını ölçer.

        Args:
            method (str): İstemci metodu adı (get, post, patch).
            url (str): İstek adresi.
            data (Optional[dict]): İstek gövdesi veya sorgu parametreleri.
            **extra (Any): İstemciye aktarılan ek başlıklar.

        Returns:
            int: Sorgu sayısı.
        """
        kwargs = {'format': 'json'} if method in ('post', 'patch') else {}
        with CaptureQueriesContext(connection) as context:
            response = getattr(self.client, method)(url, data, **kwargs, **extra)
        self.assertLess(response.status_code, 400, getattr(response, 'data', None))
        return len(context.captured_queries)

    def assert_constant_list(self, url, grow, **params):
        """
        Liste adresinin büyütme öncesi ve sonrası sorgu sayısını iki dilde karşılaştırır.

        Args:
            url (str): Liste adresi.
            grow (Callable): Farklı ilişkili kayıtlarla veri ekleyen fonksiyon.
            **params (Any): Sorgu parametreleri.
        """
        for extra in self.LANGUAGES:
            baseline = self.measure('get', url, params, **extra)
            grow()
            grown = self.measure('get', url, params, **extra)
            self.assertEqual(grown, baseline, extra)

    def test_admin_inquiry_list_has_no_n_plus_one(self):
        """
        Admin hızlı talep listesinde hizmet için N+1 sorgu oluşmadığını doğrular.

        Senaryo:
        - Farklı hizmetlere ait 1 hızlı talepte sorgu sayısı ölçülür; farklı çevirili hizmetlerle 10 talebe çıkarılır.

        Beklenti:
        - Sorgu sayısı Türkçe ve İngilizce isteklerde değişmemelidir.
        """
        self.client.force_authenticate(make_user(is_staff=True))
        ServiceInquiryFactory(service=make_bilingual_service())

        def grow():
            for _index in range(9):
                ServiceInquiryFactory(service=make_bilingual_service())

        self.assert_constant_list(reverse('care-admin:inquiry-list'), grow)

    def test_applicant_request_detail_has_no_n_plus_one(self):
        """
        Başvuru sahibinin talep detayında sorgu sayısının diğer kayıtlardan etkilenmediğini doğrular.

        Senaryo:
        - Kullanıcının 1 talebi varken detay ölçülür; farklı hizmetli talepler daha eklenip aynı detay tekrar ölçülür.

        Beklenti:
        - Sorgu sayısı Türkçe ve İngilizce isteklerde değişmemelidir.
        """
        user = make_user()
        self.client.force_authenticate(user)
        care_request = make_care_request(applicant=user, service=make_bilingual_service())
        url = reverse('care:request-detail', args=[care_request.pk])
        for extra in self.LANGUAGES:
            baseline = self.measure('get', url, **extra)
            for _index in range(5):
                make_care_request(applicant=user, service=make_bilingual_service())
            self.assertEqual(self.measure('get', url, **extra), baseline, extra)

    def test_admin_request_detail_has_no_n_plus_one(self):
        """
        Admin talep detayında sorgu sayısının diğer talepler ve hizmet çevirilerinden bağımsız olduğunu doğrular.

        Senaryo:
        - Tek talepte detay ölçülür; başka kullanıcı ve hizmetlerle talepler eklenip tekrar ölçülür.

        Beklenti:
        - Sorgu sayısı Türkçe ve İngilizce isteklerde değişmemelidir.
        """
        self.client.force_authenticate(make_user(is_staff=True))
        care_request = make_care_request(service=make_bilingual_service())
        url = reverse('care-admin:request-detail', args=[care_request.pk])
        for extra in self.LANGUAGES:
            baseline = self.measure('get', url, **extra)
            for _index in range(5):
                make_care_request(service=make_bilingual_service())
            self.assertEqual(self.measure('get', url, **extra), baseline, extra)

    def test_admin_request_status_update_has_no_n_plus_one(self):
        """
        Admin durum güncelleme yanıtının sorgu sayısının kayıt sayısından bağımsız olduğunu doğrular.

        Senaryo:
        - Tek talepte PATCH ile durum güncellenir ve sorgu sayısı ölçülür.
        - Başka kullanıcı ve hizmetlerle talepler eklenip başka bir talep güncellenir.

        Beklenti:
        - Sorgu sayısı Türkçe ve İngilizce isteklerde değişmemelidir.
        """
        self.client.force_authenticate(make_user(is_staff=True))
        for extra in self.LANGUAGES:
            first = make_care_request(service=make_bilingual_service())
            baseline = self.measure(
                'patch', reverse('care-admin:request-detail', args=[first.pk]), {'status': 'reviewing'}, **extra,
            )
            for _index in range(5):
                make_care_request(service=make_bilingual_service())
            second = make_care_request(service=make_bilingual_service())
            grown = self.measure(
                'patch', reverse('care-admin:request-detail', args=[second.pk]), {'status': 'reviewing'}, **extra,
            )
            self.assertEqual(grown, baseline, extra)

    def test_applicant_request_create_has_no_n_plus_one(self):
        """
        Talep oluşturma yanıtının sorgu sayısının mevcut talep ve hizmet sayısından bağımsız olduğunu doğrular.

        Senaryo:
        - Kullanıcının hiç talebi yokken talep oluşturulur ve sorgu sayısı ölçülür.
        - Farklı hizmetlerde 9 talep eklenip yeni bir talep daha oluşturulur.

        Beklenti:
        - Sorgu sayısı Türkçe ve İngilizce isteklerde değişmemelidir.
        """
        user = make_user()
        self.client.force_authenticate(user)
        counter = iter(range(1000))

        def payload():
            data = care_request_data(elder_full_name=f'Yaşlı {next(counter)}', service=make_bilingual_service().pk, consent=True)
            data['preferred_date'] = data['preferred_date'].isoformat()
            return data

        with patch.dict(SimpleRateThrottle.THROTTLE_RATES, {CareRequestCreateRateThrottle.scope: '1000/minute'}):
            for extra in self.LANGUAGES:
                baseline = self.measure('post', reverse('care:request-list'), payload(), **extra)
                for _index in range(9):
                    make_care_request(
                        applicant=user, service=make_bilingual_service(), status=CareRequest.Status.COMPLETED,
                    )
                grown = self.measure('post', reverse('care:request-list'), payload(), **extra)
                self.assertEqual(grown, baseline, extra)

    def test_admin_request_list_search_and_filters_have_no_n_plus_one(self):
        """
        Admin talep listesinde arama, filtre ve sıralamanın N+1 sorgu oluşturmadığını doğrular.

        Senaryo:
        - Aranan şehirdeki 1 talepte `search`, `status`, `service` ve `ordering` parametreleriyle ölçüm yapılır.
        - Farklı kullanıcılarla eşleşen 9 talep daha eklenip tekrar ölçülür.

        Beklenti:
        - Her parametre kümesi için sorgu sayısı değişmemelidir.
        """
        self.client.force_authenticate(make_user(is_staff=True))
        service = make_bilingual_service()
        url = reverse('care-admin:request-list')
        make_care_request(service=service, city='Samsun')
        cases = (
            {'search': 'Samsun'},
            {'search': 'example.com'},
            {'status': 'new', 'service': service.pk, 'ordering': '-created_at'},
            {'ordering': 'status'},
        )
        baselines = [[self.measure('get', url, params, **extra) for extra in self.LANGUAGES] for params in cases]
        for _index in range(9):
            make_care_request(service=service, city='Samsun')
        for params, expected in zip(cases, baselines):
            grown = [self.measure('get', url, params, **extra) for extra in self.LANGUAGES]
            self.assertEqual(grown, expected, params)

    def test_dashboard_all_sources_english_has_no_n_plus_one(self):
        """
        Dashboard'un tüm kaynaklar ve İngilizce dilinde veri miktarından bağımsız sorgu çalıştırdığını doğrular.

        Senaryo:
        - Çevirili hizmetlere bağlı talep ve hızlı talepler varken `days=90&source=all` ile ölçülür.
        - Yeni hizmet, talep ve hızlı talepler eklenip tekrar ölçülür.

        Beklenti:
        - Sorgu sayısı değişmemelidir.
        """
        self.client.force_authenticate(make_user(is_staff=True))
        url = reverse('care-admin:dashboard')

        def add_records():
            service = make_bilingual_service()
            make_care_request(service=service)
            ServiceInquiryFactory(service=service)

        add_records()
        params = {'days': 90, 'source': 'all'}
        baseline = [self.measure('get', url, params, **extra) for extra in self.LANGUAGES]
        for _index in range(6):
            add_records()
        grown = [self.measure('get', url, params, **extra) for extra in self.LANGUAGES]

        self.assertEqual(grown, baseline)
