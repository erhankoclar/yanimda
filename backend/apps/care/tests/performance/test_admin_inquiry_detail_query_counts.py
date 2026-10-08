from django.db import connection
from django.test.utils import CaptureQueriesContext
from django.urls import reverse
from rest_framework.test import APITestCase

from apps.care.factories import ServiceInquiryFactory
from apps.care.tests.factories import make_user
from apps.geo.factories import NeighborhoodFactory


class AdminInquiryDetailQueryCountTests(APITestCase):
    def test_detail_query_count_is_constant(self):
        """
        Detay isteğinin tablodaki kayıt sayısından bağımsız sabit sorguyla çalıştığını doğrular.

        Senaryo:
        - Bir talepli durumda detay isteğinin sorgu sayısı ölçülür.
        - 15 talep daha eklenip başka bir talebin detayı yeniden ölçülür.

        Beklenti:
        - Sorgu sayısı değişmemeli ve en fazla 6 olmalıdır.
        """
        self.client.force_authenticate(make_user(is_staff=True))
        first = ServiceInquiryFactory(neighborhood=NeighborhoodFactory())
        with CaptureQueriesContext(connection) as baseline:
            self.client.get(reverse('care-admin:inquiry-detail', args=[first.pk]))

        for _index in range(15):
            ServiceInquiryFactory(neighborhood=NeighborhoodFactory())
        last = ServiceInquiryFactory(neighborhood=NeighborhoodFactory())
        with CaptureQueriesContext(connection) as after:
            self.client.get(reverse('care-admin:inquiry-detail', args=[last.pk]))

        self.assertEqual(len(after.captured_queries), len(baseline.captured_queries))
        self.assertLessEqual(len(after.captured_queries), 6)
