from django.db import connection
from django.test.utils import CaptureQueriesContext
from django.urls import reverse
from rest_framework.test import APITestCase

from apps.care.factories import CareRequestFactory, ServiceInquiryFactory, ServiceTypeFactory
from apps.care.tests.factories import make_user
from apps.geo.factories import DistrictFactory, NeighborhoodFactory


class MapQueryCountTests(APITestCase):
    """Harita endpoint'inin sorgu sayısının veri hacminden bağımsız olduğunu doğrular."""

    def setUp(self):
        """Admin olarak oturum açar."""
        self.client.force_authenticate(make_user(is_staff=True))

    def count_queries(self):
        """
        Harita isteğinde çalışan sorgu sayısını ölçer.

        Returns:
            int: SQL sorgusu sayısı.
        """
        with CaptureQueriesContext(connection) as context:
            self.client.get(reverse('care-admin:map'))
        return len(context.captured_queries)

    def test_query_count_is_constant(self):
        """
        Kayıt, ilçe, mahalle ve hizmet arttığında sorgu sayısının değişmediğini doğrular.

        Senaryo:
        - Bir kayıtla sorgu sayısı ölçülür.
        - Birçok ilçe, mahalle, hizmet ve kayıt eklenip tekrar ölçülür.

        Beklenti:
        - Sorgu sayısı aynı kalmalıdır.
        """
        CareRequestFactory()
        baseline = self.count_queries()

        for _index in range(4):
            district = DistrictFactory()
            for _inner in range(3):
                neighborhood = NeighborhoodFactory(district=district)
                service = ServiceTypeFactory()
                ServiceInquiryFactory(service=service, neighborhood=neighborhood)
                CareRequestFactory(service=service, neighborhood=neighborhood)

        self.assertEqual(self.count_queries(), baseline)
