from datetime import timedelta

from django.core.cache import cache
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext
from rest_framework import status
from rest_framework.test import APITestCase

from apps.care import conf
from apps.care.models import CareRequest
from apps.care.tests.factories import care_request_data, make_care_request, make_service, make_user


class ServiceListApiTests(APITestCase):
    def test_lists_only_active_services_in_order_without_login(self):
        """
        Hizmet listesinin girişsiz erişilebildiğini ve yalnızca aktif hizmetleri sıralı döndürdüğünü doğrular.

        Senaryo:
        - Sıra numaraları ters iki aktif ve bir pasif hizmet oluşturulur.
        - Liste endpoint'i kimlik doğrulamasız çağrılır.

        Beklenti:
        - 200 dönmeli, sayfalanmamış listede yalnızca aktifler sıra numarasına göre bulunmalıdır.
        """
        second = make_service(sort_order=20)
        first = make_service(sort_order=10)
        make_service(is_active=False)

        response = self.client.get(reverse('care:service-list'))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual([item['id'] for item in response.data], [first.id, second.id])
        self.assertEqual(set(response.data[0]), {'id', 'name', 'slug', 'description', 'icon'})


class CareRequestApiTestCase(APITestCase):
    def setUp(self):
        """Throttle sayaçlarını sıfırlar, oturum açmış başvuru sahibi ve aktif hizmet hazırlar."""
        cache.clear()
        self.user = make_user()
        self.service = make_service()
        self.client.force_authenticate(self.user)

    def payload(self, **overrides):
        """
        Talep oluşturma için geçerli JSON gövdesini döndürür.

        Args:
            **overrides (Any): Varsayılan alanları ezen değerler.

        Returns:
            dict[str, Any]: İstek gövdesi.
        """
        data = care_request_data()
        data['preferred_date'] = data['preferred_date'].isoformat()
        data['neighborhood'] = data['neighborhood'].pk
        return {**data, 'service': self.service.id, 'consent': True, **overrides}

    def create(self, **overrides):
        """
        Talep oluşturma endpoint'ini çağırır.

        Args:
            **overrides (Any): Gövde alanlarını ezen değerler.

        Returns:
            Response: Endpoint yanıtı.
        """
        return self.client.post(reverse('care:request-list'), self.payload(**overrides), format='json')


class CareRequestCreateApiTests(CareRequestApiTestCase):
    def test_create_request_for_current_user(self):
        """
        Geçerli verilerle talebin oturumdaki kullanıcı adına oluşturulduğunu doğrular.

        Senaryo:
        - Telefonu boşluklu girilmiş geçerli bir talep gönderilir.

        Beklenti:
        - 201 dönmeli; talep `new` durumunda, kullanıcıya bağlı ve onay zamanı kayıtlı olmalıdır.
        - Telefon yalnızca rakamlara normalleştirilmeli, yanıtta hizmet detayı bulunmalıdır.
        """
        response = self.create(contact_phone='0555 111 22 33')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        care_request = CareRequest.objects.get()
        self.assertEqual(care_request.applicant, self.user)
        self.assertEqual(care_request.status, CareRequest.Status.NEW)
        self.assertIsNotNone(care_request.consent_given_at)
        self.assertEqual(care_request.contact_phone, '05551112233')
        self.assertEqual(response.data['service_detail']['id'], self.service.id)
        self.assertEqual(response.data['status_display'], gettext('New'))
        self.assertNotIn('consent', response.data)

    def test_create_with_alternate_contact(self):
        """Alternatif kişi adı ve telefonu birlikte verildiğinde talebin oluştuğunu doğrular."""
        response = self.create(alternate_contact_name='Mehmet Yılmaz', alternate_contact_phone='+90 555 000 11 22')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(CareRequest.objects.get().alternate_contact_phone, '+905550001122')

    def test_rejects_past_date(self):
        """Geçmiş tarihli talebin reddedildiğini doğrular (hata yolu)."""
        yesterday = timezone.localdate() - timedelta(days=1)

        response = self.create(preferred_date=yesterday.isoformat())

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['preferred_date'], [gettext('The preferred date cannot be in the past.')])

    def test_rejects_date_too_far_ahead(self):
        """
        İzin verilen süreden ileri tarihli talebin reddedildiğini doğrular (sınır değer).

        Senaryo:
        - Tarih, izin verilen en ileri günün bir gün sonrası olarak gönderilir.

        Beklenti:
        - 400 dönmeli ve hata gün sayısını içermelidir.
        """
        too_far = timezone.localdate() + timedelta(days=conf.MAX_PREFERRED_DAYS_AHEAD + 1)

        response = self.create(preferred_date=too_far.isoformat())

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        expected = gettext('The preferred date can be at most %(days)d days ahead.') % {
            'days': conf.MAX_PREFERRED_DAYS_AHEAD,
        }
        self.assertEqual(response.data['preferred_date'], [expected])

    def test_rejects_missing_consent(self):
        """Kişisel veri onayı verilmeden talep oluşturulamadığını doğrular (hata yolu)."""
        response = self.create(consent=False)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['consent'], [gettext('You must accept the processing of personal data.')])
        self.assertFalse(CareRequest.objects.exists())

    def test_rejects_inactive_service(self):
        """Pasif hizmet için talep oluşturulamadığını doğrular (hata yolu)."""
        inactive = make_service(is_active=False)

        response = self.create(service=inactive.id)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('service', response.data)

    def test_rejects_invalid_phone(self):
        """
        Geçersiz telefon numaralarının reddedildiğini doğrular (hata yolu).

        Senaryo:
        - Harf içeren ve çok kısa telefonlarla talep denenir.

        Beklenti:
        - Her ikisi de 400 ve `contact_phone` hatası vermelidir.
        """
        for phone in ('0555abc1122', '12345'):
            response = self.create(contact_phone=phone)

            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertEqual(response.data['contact_phone'], [gettext('Enter a valid phone number.')])

    def test_alternate_name_requires_phone(self):
        """
        Alternatif kişi adının telefonsuz, telefonunun adsız verilemediğini doğrular (çapraz alan kuralı).

        Senaryo:
        - Önce yalnızca ad, sonra yalnızca telefon gönderilir.

        Beklenti:
        - Her seferinde eksik olan alan için hata dönmelidir.
        """
        only_name = self.create(alternate_contact_name='Mehmet')
        only_phone = self.create(alternate_contact_phone='05550001122')

        self.assertEqual(only_name.data['alternate_contact_phone'], [gettext('Enter the phone of the alternate contact.')])
        self.assertEqual(only_phone.data['alternate_contact_name'], [gettext('Enter the name of the alternate contact.')])

    def test_rejects_age_out_of_range(self):
        """Yaşlı yaşı aralık dışında olduğunda talebin reddedildiğini doğrular (sınır değer)."""
        response = self.create(elder_age=39)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('elder_age', response.data)


class CareRequestReadApiTests(CareRequestApiTestCase):
    def test_list_returns_only_own_requests_newest_first(self):
        """
        Listenin yalnızca kullanıcının kendi taleplerini en yeniden eskiye döndürdüğünü doğrular.

        Senaryo:
        - Kullanıcı için iki, başka kullanıcı için bir talep oluşturulur.

        Beklenti:
        - Sayfalı yanıtta yalnızca kullanıcının iki talebi yeni olan önce gelmelidir.
        """
        older = make_care_request(applicant=self.user)
        newer = make_care_request(applicant=self.user)
        CareRequest.objects.filter(pk=older.pk).update(created_at=timezone.now() - timedelta(days=1))
        make_care_request()

        response = self.client.get(reverse('care:request-list'))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 2)
        self.assertEqual([item['id'] for item in response.data['results']], [newer.id, older.id])

    def test_detail_returns_own_request(self):
        """Kullanıcının kendi talebinin detayını görebildiğini doğrular."""
        care_request = make_care_request(applicant=self.user)

        response = self.client.get(reverse('care:request-detail', args=[care_request.pk]))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['elder_full_name'], care_request.elder_full_name)
        self.assertEqual(response.data['status'], CareRequest.Status.NEW)


class DuplicateOpenRequestApiTests(CareRequestApiTestCase):
    def duplicate_message(self, elder='Fatma Yılmaz'):
        """
        Mükerrer talep hata mesajını etkin dilde oluşturur.

        Args:
            elder (str): Yaşlının adı soyadı.

        Returns:
            str: Beklenen hata mesajı.
        """
        return gettext(
            'You already have an open request for this service for %(elder)s. '
            'You can apply again when it is completed or cancelled.'
        ) % {'elder': elder}

    def test_rejects_second_open_request_for_same_elder_and_service(self):
        """
        Aynı yaşlı için aynı hizmete ikinci açık talebin reddedildiğini doğrular.

        Senaryo:
        - Bir talep oluşturulur.
        - Aynı hizmet ve yaşlı adı (farklı harf büyüklüğü ve boşlukla) tekrar gönderilir.

        Beklenti:
        - İkinci istek 400 dönmeli, hata `service` alanında olmalı ve tek talep kalmalıdır.
        """
        self.create()

        response = self.create(elder_full_name='  fatma YILMAZ ')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['service'], [self.duplicate_message('fatma YILMAZ')])
        self.assertEqual(CareRequest.objects.count(), 1)

    def test_allows_same_service_for_another_elder(self):
        """Aynı hizmetin başka bir yaşlı için istenebildiğini doğrular."""
        self.create()

        response = self.create(elder_full_name='Ahmet Yılmaz')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_allows_another_service_for_same_elder(self):
        """Aynı yaşlı için farklı bir hizmet istenebildiğini doğrular."""
        self.create()

        response = self.create(service=make_service().id)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_allows_reapply_after_request_is_closed(self):
        """
        Tamamlanan veya iptal edilen talepten sonra aynı hizmete yeniden başvurulabildiğini doğrular.

        Senaryo:
        - Talep oluşturulup tamamlandı yapılır, yeniden başvurulur.
        - Yeni talep iptal edilip tekrar başvurulur.

        Beklenti:
        - Her iki yeniden başvuru da 201 dönmelidir.
        """
        self.create()
        CareRequest.objects.update(status=CareRequest.Status.COMPLETED)
        self.assertEqual(self.create().status_code, status.HTTP_201_CREATED)

        CareRequest.objects.filter(status=CareRequest.Status.NEW).update(status=CareRequest.Status.CANCELLED)

        self.assertEqual(self.create().status_code, status.HTTP_201_CREATED)

    def test_other_applicants_request_does_not_block(self):
        """Başka bir kullanıcının aynı yaşlı ve hizmet için açık talebinin engel olmadığını doğrular."""
        make_care_request(service=self.service)

        self.assertEqual(self.create().status_code, status.HTTP_201_CREATED)

    def test_database_constraint_turns_race_into_validation_error(self):
        """
        Eşzamanlı iki isteğin doğrulamayı birlikte geçmesi durumunda 500 yerine 400 döndüğünü doğrular (yarış durumu).

        Senaryo:
        - Uygulama düzeyindeki mükerrer kontrolü devre dışı bırakılarak iki talep gönderilir.

        Beklenti:
        - Veritabanı kısıtı ikinci talebi engellemeli; yanıt 400 ve `service` hatası olmalıdır.
        """
        from unittest.mock import patch


        with patch('apps.care.services.care_request_service.has_open_duplicate', return_value=False):
            self.create()
            response = self.create()

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['service'], [self.duplicate_message()])
        self.assertEqual(CareRequest.objects.count(), 1)
