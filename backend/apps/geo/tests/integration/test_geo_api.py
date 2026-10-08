from django.urls import reverse
from rest_framework.test import APITestCase

from apps.geo.models import District
from apps.geo.services.location_service import create_default_locations


def make_data():
    """
    Sırası bilerek karışık küçük bir ilçe ağacı üretir.

    Returns:
        list[dict]: Üç ilçe ve mahalleleri.
    """
    return [
        {'osm_id': 3, 'name': 'Ümraniye', 'slug': 'umraniye', 'neighborhoods': [
            {'osm_id': 31, 'name': 'Zafer Mahallesi'},
        ]},
        {'osm_id': 1, 'name': 'Çatalca', 'slug': 'catalca', 'neighborhoods': [
            {'osm_id': 12, 'name': 'Ören Mahallesi'},
            {'osm_id': 11, 'name': 'Ağaçlı Mahallesi'},
            {'osm_id': 13, 'name': 'Çiftlik Mahallesi'},
        ]},
        {'osm_id': 2, 'name': 'Bağcılar', 'slug': 'bagcilar', 'neighborhoods': [
            {'osm_id': 21, 'name': 'Merkez Mahallesi'},
        ]},
    ]


class GeoApiTests(APITestCase):
    def setUp(self):
        """Test verisini servis üzerinden yükler."""
        create_default_locations(make_data())

    def test_district_list_in_turkish_order(self):
        """
        İlçe listesinin Türkçe sırada ve beklenen alanlarla döndüğünü doğrular.

        Senaryo:
        - Üç ilçe yüklenir, anonim istemciyle liste istenir.

        Beklenti:
        - 200 dönmeli; sıra Bağcılar, Çatalca, Ümraniye; alanlar id, name, slug, osm_id olmalıdır.
        """
        response = self.client.get(reverse('geo:district-list'))

        self.assertEqual(response.status_code, 200)
        self.assertEqual([item['name'] for item in response.json()], ['Bağcılar', 'Çatalca', 'Ümraniye'])
        self.assertEqual(set(response.json()[0]), {'id', 'name', 'slug', 'osm_id'})

    def test_neighborhood_list_only_that_district_in_order(self):
        """
        Mahalle listesinin yalnızca ilgili ilçeyi içerdiğini ve sıralı olduğunu doğrular.

        Senaryo:
        - Çatalca ilçesinin mahalleleri istenir.

        Beklenti:
        - Yalnızca 3 mahalle Türkçe sırada gelmeli; alanlar id, name, osm_id olmalıdır.
        """
        district = District.objects.get(osm_id=1)

        response = self.client.get(reverse('geo:neighborhood-list', args=[district.id]))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            [item['name'] for item in response.json()],
            ['Ağaçlı Mahallesi', 'Çiftlik Mahallesi', 'Ören Mahallesi'],
        )
        self.assertEqual(set(response.json()[0]), {'id', 'name', 'osm_id'})

    def test_unknown_district_returns_empty_list(self):
        """
        Bilinmeyen ilçe kimliğinde boş liste döndüğünü doğrular.

        Senaryo:
        - Var olmayan bir ilçe kimliğiyle mahalle listesi istenir.

        Beklenti:
        - 200 durum kodu ve boş liste dönmelidir.
        """
        response = self.client.get(reverse('geo:neighborhood-list', args=[999999]))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), [])
