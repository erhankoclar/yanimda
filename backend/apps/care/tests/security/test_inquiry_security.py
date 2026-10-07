from unittest.mock import patch

from django.core.cache import cache
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework.throttling import SimpleRateThrottle

from apps.care.models import ServiceInquiry
from apps.care.tests.factories import make_service, make_user
from apps.care.throttles import InquiryCreateRateThrottle


class InquirySecurityTests(APITestCase):
    def setUp(self):
        """Throttle sayaçlarını sıfırlar ve geçerli gövdeyi hazırlar."""
        cache.clear()
        self.url = reverse('care:inquiry-create')
        self.payload = {
            'full_name': 'Deneme Kişi', 'email': 'deneme@example.com', 'service': make_service().id,
            'message': 'Annem için refakat desteği istiyoruz.', 'consent': True,
        }

    def test_honeypot_blocks_bots(self):
        """
        Gizli spam tuzağı alanı doldurulduğunda talebin kaydedilmediğini doğrular.

        Senaryo:
        - `website` alanı dolu bir istek gönderilir.

        Beklenti:
        - 400 dönmeli ve kayıt oluşmamalıdır.
        """
        response = self.client.post(self.url, {**self.payload, 'website': 'http://spam.example'}, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(ServiceInquiry.objects.exists())

    def test_is_throttled_per_ip(self):
        """
        Hızlı formun IP başına sınırlandığını doğrular (spam ve kötüye kullanım koruması).

        Senaryo:
        - Oran saatte 1 yapılır ve iki talep gönderilir.

        Beklenti:
        - İkinci talep 429 dönmeli ve yalnızca bir kayıt oluşmalıdır.
        """
        with patch.dict(SimpleRateThrottle.THROTTLE_RATES, {InquiryCreateRateThrottle.scope: '1/hour'}):
            self.client.post(self.url, self.payload, format='json')
            second = self.client.post(self.url, self.payload, format='json')

        self.assertEqual(second.status_code, status.HTTP_429_TOO_MANY_REQUESTS)
        self.assertEqual(ServiceInquiry.objects.count(), 1)

    def test_stale_token_does_not_block_public_form(self):
        """Tarayıcıda kalmış geçersiz bir token'ın herkese açık formu engellemediğini doğrular."""
        self.client.credentials(HTTP_AUTHORIZATION='Bearer gecersiz.token.degeri')

        response = self.client.post(self.url, self.payload, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_listing_inquiries_requires_admin(self):
        """
        Talep listesinin yalnızca yöneticilere açık olduğunu doğrular (kişisel veri koruması).

        Senaryo:
        - Liste önce kimliksiz, sonra standart kullanıcıyla istenir.

        Beklenti:
        - 401 ve 403 dönmelidir.
        """
        url = reverse('care-admin:inquiry-list')

        self.assertEqual(self.client.get(url).status_code, status.HTTP_401_UNAUTHORIZED)
        self.client.force_authenticate(make_user())
        self.assertEqual(self.client.get(url).status_code, status.HTTP_403_FORBIDDEN)

    def test_public_endpoint_is_create_only(self):
        """Herkese açık uç noktada talepleri listelemenin kapalı olduğunu doğrular (veri sızıntısı)."""
        self.client.post(self.url, self.payload, format='json')

        self.assertEqual(self.client.get(self.url).status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
