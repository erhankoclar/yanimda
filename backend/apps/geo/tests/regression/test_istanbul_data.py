from collections import Counter

from django.test import SimpleTestCase

from apps.geo.services.location_service import load_location_data


class IstanbulDataRegressionTests(SimpleTestCase):
    def test_district_count_and_unique_slugs(self):
        """
        Veri dosyasında 39 ilçe bulunduğunu ve slug değerlerinin benzersiz olduğunu doğrular.

        Senaryo:
        - istanbul.json okunur.

        Beklenti:
        - 39 ilçe olmalı; slug ve ilçe osm_id değerleri tekrar etmemelidir.
        """
        districts = load_location_data()

        self.assertEqual(len(districts), 39)
        self.assertEqual(len({item['slug'] for item in districts}), 39)
        self.assertEqual(len({item['osm_id'] for item in districts}), 39)

    def test_neighborhoods_belong_to_exactly_one_district(self):
        """
        Her mahallenin tek bir ilçeye ait olduğunu ve osm_id değerlerinin benzersiz olduğunu doğrular.

        Senaryo:
        - Tüm ilçelerin mahalle osm_id değerleri sayılır.

        Beklenti:
        - Hiçbir osm_id birden fazla geçmemeli, ilçe kimlikleriyle çakışmamalı, toplam 964 olmalıdır.
        """
        districts = load_location_data()
        neighborhood_ids = [entry['osm_id'] for item in districts for entry in item['neighborhoods']]
        duplicates = [key for key, count in Counter(neighborhood_ids).items() if count > 1]

        self.assertEqual(duplicates, [])
        self.assertEqual(len(neighborhood_ids), 964)
        self.assertFalse(set(neighborhood_ids) & {item['osm_id'] for item in districts})
