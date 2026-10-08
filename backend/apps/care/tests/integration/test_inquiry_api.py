from django.core.cache import cache
from django.urls import reverse
from django.utils.translation import gettext
from rest_framework import status
from rest_framework.test import APITestCase

from apps.care.models import ServiceInquiry
from apps.care.tests.factories import make_service, make_user
from apps.geo.factories import NeighborhoodFactory


class InquiryApiTestCase(APITestCase):
    def setUp(self):
        """Throttle sayaçlarını sıfırlar ve aktif bir hizmet hazırlar."""
        cache.clear()
        self.service = make_service()
        self.neighborhood = NeighborhoodFactory()
        self.url = reverse('care:inquiry-create')

    def payload(self, **overrides):
        """
        Geçerli hızlı talep gövdesini döndürür.

        Args:
            **overrides (Any): Varsayılan alanları ezen değerler.

        Returns:
            dict[str, Any]: İstek gövdesi.
        """
        return {
            'full_name': 'Deneme Kişi',
            'email': 'deneme@example.com',
            'service': self.service.id,
            'neighborhood': self.neighborhood.id,
            'message': 'Annem için haftada iki gün refakat desteği istiyoruz.',
            'consent': True,
            'website': '',
            **overrides,
        }


class InquiryCreateApiTests(InquiryApiTestCase):
    def test_saves_inquiry_without_account(self):
        """
        Hesap olmadan gönderilen talebin kalıcı olarak kaydedildiğini doğrular.

        Senaryo:
        - Kimlik doğrulamasız geçerli bir talep gönderilir.

        Beklenti:
        - 201 dönmeli; kayıt veritabanında olmalı, onay zamanı ve normalleştirilmiş e-posta saklanmalıdır.
        - Yanıt kayıt kimliğini ve hizmet bilgisini içermelidir.
        """
        response = self.client.post(self.url, self.payload(email=' Deneme@Example.COM ', full_name='  Deneme   Kişi '), format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        inquiry = ServiceInquiry.objects.get(pk=response.data['id'])
        self.assertEqual(inquiry.email, 'deneme@example.com')
        self.assertEqual(inquiry.full_name, 'Deneme Kişi')
        self.assertIsNotNone(inquiry.consent_given_at)
        self.assertEqual(response.data['service_detail']['id'], self.service.id)

    def test_required_fields(self):
        """
        Zorunlu alanlar olmadan talebin reddedildiğini doğrular (hata yolu).

        Senaryo:
        - Boş gövde gönderilir.

        Beklenti:
        - 400 dönmeli; ad, e-posta, hizmet, mahalle, açıklama ve onay alanlarında hata olmalı, kayıt oluşmamalıdır.
        """
        response = self.client.post(self.url, {}, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(set(response.data), {'full_name', 'email', 'service', 'neighborhood', 'message', 'consent'})
        self.assertFalse(ServiceInquiry.objects.exists())

    def test_rejects_invalid_values(self):
        """
        Geçersiz değerlerin alanlarına göre reddedildiğini doğrular (hata yolu).

        Senaryo:
        - Tek harfli ad, geçersiz e-posta, kısa açıklama ve verilmemiş onayla talep gönderilir.

        Beklenti:
        - Her alan için çevrilmiş hata mesajı dönmelidir.
        """
        response = self.client.post(self.url, self.payload(
            full_name=' A ', email='gecersiz', message='kısa', consent=False,
        ), format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['full_name'], [gettext('Enter your name and surname.')])
        self.assertIn('email', response.data)
        self.assertEqual(
            response.data['message'],
            [gettext('Please describe the need in at least %(count)d characters.') % {'count': 10}],
        )
        self.assertEqual(response.data['consent'], [gettext('You must accept the processing of personal data.')])

    def test_rejects_too_long_message(self):
        """2000 karakteri aşan açıklamanın reddedildiğini doğrular (sınır değer)."""
        response = self.client.post(self.url, self.payload(message='a' * 2001), format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('message', response.data)

    def test_rejects_inactive_service(self):
        """Pasif hizmet için talep gönderilemediğini doğrular (hata yolu)."""
        response = self.client.post(self.url, self.payload(service=make_service(is_active=False).id), format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('service', response.data)


class AdminInquiryListApiTests(InquiryApiTestCase):
    def test_admin_sees_inquiries_newest_first_and_can_search(self):
        """
        Yöneticinin kayıtlı talepleri en yeniden eskiye görüp arayabildiğini doğrular.

        Senaryo:
        - İki talep gönderilir ve admin listesi çağrılır, ardından e-postaya göre aranır.

        Beklenti:
        - İki talep yeni olan önce listelenmeli, arama yalnızca eşleşeni döndürmelidir.
        """
        first = self.client.post(self.url, self.payload(), format='json').data['id']
        second = self.client.post(self.url, self.payload(email='ikinci@example.com'), format='json').data['id']
        self.client.force_authenticate(make_user(is_staff=True))

        listing = self.client.get(reverse('care-admin:inquiry-list')).data
        searched = self.client.get(reverse('care-admin:inquiry-list'), {'search': 'ikinci@'}).data

        self.assertEqual([row['id'] for row in listing['results']], [second, first])
        self.assertEqual([row['id'] for row in searched['results']], [second])
