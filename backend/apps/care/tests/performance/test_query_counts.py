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

    def test_service_list_uses_single_query(self):
        """Hizmet listesinin hizmet sayısından bağımsız tek sorguyla döndüğünü doğrular."""
        for _index in range(5):
            make_service()

        with self.assertNumQueries(1):
            self.client.get(reverse('care:service-list'))
