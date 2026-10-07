from django.db import connection
from django.test.utils import CaptureQueriesContext
from django.urls import reverse
from rest_framework.test import APITestCase

from apps.care.tests.factories import make_care_request, make_user


class AdminUserQueryCountTests(APITestCase):
    def test_user_list_query_count_is_constant(self):
        """
        Admin kullanıcı listesinde talep sayısı için N+1 sorgu oluşmadığını doğrular.

        Senaryo:
        - Talepli 1 kullanıcıyla sorgu sayısı ölçülür; 10 kullanıcıya çıkarılıp tekrar ölçülür.

        Beklenti:
        - Sorgu sayısı değişmemelidir.
        """
        self.client.force_authenticate(make_user(is_staff=True))
        url = reverse('accounts-admin:user-list')
        make_care_request()
        with CaptureQueriesContext(connection) as baseline:
            self.client.get(url)
        for _index in range(9):
            make_care_request()

        with CaptureQueriesContext(connection) as grown:
            self.client.get(url)

        self.assertEqual(len(grown.captured_queries), len(baseline.captured_queries))
