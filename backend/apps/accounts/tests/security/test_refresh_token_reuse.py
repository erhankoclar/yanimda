from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

User = get_user_model()

PASSWORD = 'Yanimda-Guclu-2026'


class RefreshTokenReuseTests(APITestCase):
    def setUp(self):
        """Throttle sayaçlarını sıfırlar, kullanıcı oluşturur ve token çifti alır."""
        cache.clear()
        User.objects.create_user(email='ayse@example.com', password=PASSWORD)
        self.refresh = self.client.post(
            reverse('accounts:token'), {'email': 'ayse@example.com', 'password': PASSWORD}, format='json',
        ).data['refresh']

    def refresh_with(self, token):
        """
        Verilen refresh token ile yenileme endpoint'ini çağırır.

        Args:
            token (str): Refresh token.

        Returns:
            Response: Endpoint yanıtı.
        """
        return self.client.post(reverse('accounts:token-refresh'), {'refresh': token}, format='json')

    def test_rotated_refresh_token_cannot_be_reused(self):
        """
        Döndürülmüş eski refresh token'ın tekrar kullanılamadığını doğrular (token yeniden kullanım saldırısı).

        Senaryo:
        - Refresh token ile yenileme yapılır ve yeni token alınır.
        - Eski refresh token tekrar gönderilir.

        Beklenti:
        - İlk yenileme 200, eski token ile ikinci yenileme 401 dönmelidir.
        """
        first = self.refresh_with(self.refresh)

        reused = self.refresh_with(self.refresh)

        self.assertEqual(first.status_code, status.HTTP_200_OK)
        self.assertEqual(reused.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_logout_invalidates_refresh_token(self):
        """
        Çıkıştan sonra refresh token'ın geçersiz olduğunu doğrular.

        Senaryo:
        - Çıkış endpoint'ine refresh token gönderilir, ardından aynı token ile yenileme denenir.

        Beklenti:
        - Çıkış 200, sonraki yenileme 401 dönmelidir.
        """
        logout = self.client.post(reverse('accounts:logout'), {'refresh': self.refresh}, format='json')

        self.assertEqual(logout.status_code, status.HTTP_200_OK)
        self.assertEqual(self.refresh_with(self.refresh).status_code, status.HTTP_401_UNAUTHORIZED)

    def test_logout_rejects_invalid_token(self):
        """Geçersiz token ile çıkış isteğinin 401 döndüğünü doğrular (hata yolu)."""
        response = self.client.post(reverse('accounts:logout'), {'refresh': 'gecersiz'}, format='json')

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
