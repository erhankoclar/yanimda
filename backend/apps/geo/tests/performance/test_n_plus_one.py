from django.db import connection
from django.test.utils import CaptureQueriesContext
from django.urls import reverse
from rest_framework.test import APITestCase

from apps.geo.models import District, Neighborhood


class GeoQueryCountTests(APITestCase):
    """Liste uç noktalarının satır sayısından bağımsız sorgu sayısıyla çalıştığını doğrular."""

    def measure(self, url):
        """
        Tek bir GET isteğinin çalıştırdığı SQL sorgusu sayısını ölçer.

        Args:
            url (str): İstek adresi.

        Returns:
            int: Sorgu sayısı.
        """
        with CaptureQueriesContext(connection) as context:
            response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        return len(context.captured_queries)

    def test_district_list_query_count_constant(self):
        """
        İlçe listesi sorgu sayısının ilçe sayısından bağımsız olduğunu doğrular.

        Senaryo:
        - 1 ilçeyle, ardından 21 ilçeyle liste istenir.

        Beklenti:
        - Sorgu sayısı değişmemelidir.
        """
        District.objects.create(osm_id=1, name='A', slug='a', sort_order=1)
        url = reverse('geo:district-list')
        before = self.measure(url)
        for number in range(2, 22):
            District.objects.create(osm_id=number, name=f'D{number}', slug=f'd{number}', sort_order=number)

        self.assertEqual(self.measure(url), before)

    def test_neighborhood_list_query_count_constant(self):
        """
        Mahalle listesi sorgu sayısının mahalle sayısından bağımsız olduğunu doğrular.

        Senaryo:
        - Bir ilçede 1 mahalleyle, ardından 31 mahalleyle liste istenir.

        Beklenti:
        - Sorgu sayısı değişmemelidir.
        """
        district = District.objects.create(osm_id=1, name='A', slug='a', sort_order=1)
        Neighborhood.objects.create(osm_id=100, district=district, name='M0', sort_order=1)
        url = reverse('geo:neighborhood-list', args=[district.id])
        before = self.measure(url)
        for number in range(1, 31):
            Neighborhood.objects.create(osm_id=100 + number, district=district, name=f'M{number}', sort_order=number + 1)

        self.assertEqual(self.measure(url), before)
