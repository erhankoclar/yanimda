from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from apps.care.factories import ServiceInquiryFactory
from apps.care.tests.factories import make_user
from apps.geo.factories import NeighborhoodFactory


class AdminInquiryDetailApiTests(APITestCase):
    def setUp(self):
        """Yönetici olarak oturum açar."""
        self.client.force_authenticate(make_user(is_staff=True))

    def test_returns_full_inquiry(self):
        """
        Yöneticinin tek bir hızlı talebi tüm alanlarıyla okuyabildiğini doğrular.

        Senaryo:
        - Mahallesi olan bir hızlı talep oluşturulur.
        - Yönetici detay adresini çağırır.

        Beklenti:
        - 200 dönmeli; kimlik, ad, e-posta, hizmet, açıklama ve onay zamanı yanıtta olmalıdır.
        """
        inquiry = ServiceInquiryFactory(neighborhood=NeighborhoodFactory())

        response = self.client.get(reverse('care-admin:inquiry-detail', args=[inquiry.pk]))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], inquiry.pk)
        self.assertEqual(response.data['full_name'], inquiry.full_name)
        self.assertEqual(response.data['email'], inquiry.email)
        self.assertEqual(response.data['message'], inquiry.message)
        self.assertEqual(response.data['service']['id'], inquiry.service_id)
        self.assertIn('consent_given_at', response.data)
        self.assertIn('created_at', response.data)

    def test_includes_location(self):
        """
        Yanıtın mahalle ve ilçe bilgisini içerdiğini doğrular.

        Senaryo:
        - Bir mahalleye bağlı hızlı talep oluşturulur ve detayı istenir.

        Beklenti:
        - `location.neighborhood` ve `location.district` mahalle ve ilçe kimlikleriyle eşleşmelidir.
        """
        neighborhood = NeighborhoodFactory()
        inquiry = ServiceInquiryFactory(neighborhood=neighborhood)

        response = self.client.get(reverse('care-admin:inquiry-detail', args=[inquiry.pk]))

        self.assertEqual(response.data['location']['neighborhood']['id'], neighborhood.pk)
        self.assertEqual(response.data['location']['district']['id'], neighborhood.district_id)

    def test_location_is_null_for_old_inquiry(self):
        """
        Mahallesiz eski talepte konumun null döndüğünü doğrular.

        Senaryo:
        - Mahallesi olmayan bir hızlı talep oluşturulur ve detayı istenir.

        Beklenti:
        - 200 dönmeli ve `location` null olmalıdır.
        """
        inquiry = ServiceInquiryFactory(neighborhood=None)

        response = self.client.get(reverse('care-admin:inquiry-detail', args=[inquiry.pk]))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsNone(response.data['location'])

    def test_unknown_inquiry_returns_404(self):
        """
        Olmayan kimlikte 404 döndüğünü doğrular (hata yolu).

        Senaryo:
        - Var olmayan bir kimlikle detay adresi çağrılır.

        Beklenti:
        - 404 dönmelidir.
        """
        response = self.client.get(reverse('care-admin:inquiry-detail', args=[999999]))

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_detail_matches_list_row(self):
        """
        Detay yanıtının liste satırıyla aynı veriyi taşıdığını doğrular.

        Senaryo:
        - Bir talep oluşturulur; hem liste hem detay çağrılır.

        Beklenti:
        - Detay yanıtı liste satırına eşit olmalıdır.
        """
        inquiry = ServiceInquiryFactory(neighborhood=NeighborhoodFactory())

        row = self.client.get(reverse('care-admin:inquiry-list')).data['results'][0]
        detail = self.client.get(reverse('care-admin:inquiry-detail', args=[inquiry.pk])).data

        self.assertEqual(dict(detail), dict(row))
