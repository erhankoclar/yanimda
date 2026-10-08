from django.urls import reverse
from rest_framework.test import APITestCase

from apps.care.tests.factories import make_care_request, make_service, make_user


class CareQueryCountTests(APITestCase):
    """Liste endpoint'lerinin kayıt sayısından bağımsız sabit sorgu sayısıyla çalıştığını doğrular."""

    def setUp(self):
        """Oturum açmış kullanıcı hazırlar."""
        self.user = make_user()
        self.client.force_authenticate(self.user)

    def count_list_queries(self):
        """
        Talep listesi isteğinde çalışan sorgu sayısını ölçer.

        Returns:
            int: İstek sırasında çalıştırılan SQL sorgusu sayısı.
        """
        from django.db import connection
        from django.test.utils import CaptureQueriesContext

        with CaptureQueriesContext(connection) as context:
            self.client.get(reverse('care:request-list'))
        return len(context.captured_queries)

    def test_request_list_has_no_n_plus_one(self):
        """
        Talep listesinde hizmet bilgisi için N+1 sorgu oluşmadığını doğrular.

        Senaryo:
        - Farklı hizmetlere bağlı 1 talep varken sorgu sayısı ölçülür.
        - 10 talebe çıkarılıp tekrar ölçülür.

        Beklenti:
        - Sorgu sayısı değişmemelidir.
        """
        make_care_request(applicant=self.user)
        baseline = self.count_list_queries()
        for _index in range(9):
            make_care_request(applicant=self.user, service=make_service())

        self.assertEqual(self.count_list_queries(), baseline)

    def test_admin_request_list_has_no_n_plus_one(self):
        """
        Admin talep listesinde hizmet ve başvuru sahibi için N+1 sorgu oluşmadığını doğrular.

        Senaryo:
        - Farklı kullanıcı ve hizmetlere ait 1 talepte sorgu sayısı ölçülür, 10 talebe çıkarılıp tekrar ölçülür.

        Beklenti:
        - Sorgu sayısı değişmemelidir.
        """
        from django.db import connection
        from django.test.utils import CaptureQueriesContext

        self.client.force_authenticate(make_user(is_staff=True))
        url = reverse('care-admin:request-list')
        make_care_request()
        with CaptureQueriesContext(connection) as baseline:
            self.client.get(url)
        for _index in range(9):
            make_care_request()

        with CaptureQueriesContext(connection) as grown:
            self.client.get(url)

        self.assertEqual(len(grown.captured_queries), len(baseline.captured_queries))

    def test_dashboard_stats_query_count_is_constant(self):
        """
        Dashboard istatistiklerinin veri miktarından bağımsız sabit sayıda sorguyla hesaplandığını doğrular.

        Senaryo:
        - 1 talep ve 1 hizmetle sorgu sayısı ölçülür; 10 talep ve 10 hizmete çıkarılıp tekrar ölçülür.

        Beklenti:
        - Sorgu sayısı değişmemelidir.
        """
        from django.db import connection
        from django.test.utils import CaptureQueriesContext

        self.client.force_authenticate(make_user(is_staff=True))
        url = reverse('care-admin:stats')
        make_care_request()
        with CaptureQueriesContext(connection) as baseline:
            self.client.get(url)
        for _index in range(9):
            make_care_request()

        with CaptureQueriesContext(connection) as grown:
            self.client.get(url)

        self.assertEqual(len(grown.captured_queries), len(baseline.captured_queries))

    def test_dashboard_query_count_is_constant(self):
        """
        Dashboard verilerinin kayıt ve hizmet sayısından bağımsız sabit sorguyla hesaplandığını doğrular.

        Senaryo:
        - Az veriyle sorgu sayısı ölçülür; başvuru, hızlı talep ve hizmet sayısı artırılıp tekrar ölçülür.

        Beklenti:
        - Sorgu sayısı değişmemelidir.
        """
        from django.db import connection
        from django.test.utils import CaptureQueriesContext
        from django.utils import timezone

        from apps.care.models import ServiceInquiry

        def add_records():
            service = make_service()
            make_care_request(service=service)
            ServiceInquiry.objects.create(
                full_name='Deneme', email='d@example.com', service=service, message='Kurgusal açıklama',
                consent_given_at=timezone.now(),
            )

        self.client.force_authenticate(make_user(is_staff=True))
        url = reverse('care-admin:dashboard')
        add_records()
        with CaptureQueriesContext(connection) as baseline:
            self.client.get(url, {'days': 90})
        for _index in range(6):
            add_records()

        with CaptureQueriesContext(connection) as grown:
            self.client.get(url, {'days': 90})

        self.assertEqual(len(grown.captured_queries), len(baseline.captured_queries))

    def test_service_list_query_count_is_constant(self):
        """
        Hizmet listesinin sorgu sayısının hizmet sayısından bağımsız olduğunu doğrular.

        Senaryo:
        - Önce 2, sonra 7 hizmet varken liste istenir.

        Beklenti:
        - Her iki durumda da 2 sorgu çalışmalıdır: hizmetler ve tek seferde yüklenen çevirileri.
        """
        for count in (2, 5):
            for _index in range(count):
                make_service()

            with self.assertNumQueries(2):
                self.client.get(reverse('care:service-list'))
