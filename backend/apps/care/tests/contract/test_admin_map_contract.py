from django.urls import reverse
from rest_framework.test import APITestCase

from apps.care.tests.factories import make_user
from apps.care.tests.map_data import build_dataset

AREA_FIELDS = {'id', 'osm_id', 'name', 'count', 'by_service'}


class AdminMapContractTests(APITestCase):
    """Admin tematik haritasının bağlı olduğu yanıt şeklini sabitler."""

    def test_map_response_keys(self):
        """
        Harita yanıtının alan kümelerini doğrular.

        Senaryo:
        - Küçük veri kümesiyle harita endpoint'i çağrılır.

        Beklenti:
        - Üst düzey, hizmet, ilçe ve mahalle satırlarının anahtarları sabit kümelerle eşleşmelidir.
        """
        build_dataset()
        self.client.force_authenticate(make_user(is_staff=True))

        data = self.client.get(reverse('care-admin:map')).data

        self.assertEqual(set(data), {'total', 'services', 'districts', 'neighborhoods'})
        self.assertEqual(set(data['services'][0]), {'id', 'name', 'icon', 'count'})
        self.assertEqual(set(data['districts'][0]), AREA_FIELDS)
        self.assertEqual(set(data['neighborhoods'][0]), AREA_FIELDS | {'district_id'})
        self.assertIsInstance(data['districts'][0]['by_service'], dict)
