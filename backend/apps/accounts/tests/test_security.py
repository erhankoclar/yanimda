from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework.throttling import SimpleRateThrottle

from apps.accounts.throttles import LoginRateThrottle, RegisterRateThrottle

User = get_user_model()

PASSWORD = 'Yanimda-Guclu-2026'


class AuthSecurityTests(APITestCase):
    def setUp(self):
        """Throttle sayaçlarını sıfırlar ve standart bir kullanıcı oluşturur."""
        cache.clear()
        self.user = User.objects.create_user(email='ayse@example.com', password=PASSWORD)

    def test_me_requires_authentication(self):
        """Token olmadan profil endpoint'ine erişilemediğini doğrular (yetkisiz erişim)."""
        response = self.client.get(reverse('accounts:me'))

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_me_rejects_tampered_token(self):
        """
        İmzası bozulmuş token ile erişimin reddedildiğini doğrular.

        Senaryo:
        - Geçerli access token alınır ve son karakteri değiştirilir.

        Beklenti:
        - Profil endpoint'i 401 dönmelidir.
        """
        access = self.client.post(
            reverse('accounts:token'), {'email': 'ayse@example.com', 'password': PASSWORD}, format='json',
        ).data['access']
        tampered = access[:-1] + ('A' if access[-1] != 'A' else 'B')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {tampered}')

        response = self.client.get(reverse('accounts:me'))

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_login_with_wrong_password_fails(self):
        """Hatalı parola ile token alınamadığını doğrular (hata yolu)."""
        response = self.client.post(
            reverse('accounts:token'), {'email': 'ayse@example.com', 'password': 'yanlis'}, format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertNotIn('access', response.data)

    def test_inactive_user_cannot_login(self):
        """
        Pasif hesabın giriş yapamadığını doğrular.

        Senaryo:
        - Kullanıcı pasif hale getirilir ve doğru parola ile giriş denenir.

        Beklenti:
        - 401 dönmeli ve token verilmemelidir.
        """
        self.user.is_active = False
        self.user.save()

        response = self.client.post(
            reverse('accounts:token'), {'email': 'ayse@example.com', 'password': PASSWORD}, format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_register_cannot_grant_admin_rights(self):
        """
        Kayıt isteğine eklenen yetki alanlarının yok sayıldığını doğrular (yetki yükseltme denemesi).

        Senaryo:
        - Kayıt isteğine `is_staff` ve `is_superuser` True olarak eklenir.

        Beklenti:
        - Hesap oluşmalı ancak admin yetkisi olmamalıdır.
        """
        response = self.client.post(reverse('accounts:register'), {
            'email': 'saldirgan@example.com', 'password': PASSWORD, 'first_name': 'S', 'last_name': 'A',
            'is_staff': True, 'is_superuser': True,
        }, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        user = User.objects.get(email='saldirgan@example.com')
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)

    def test_me_patch_cannot_change_email_or_admin_flag(self):
        """
        Profil güncellemesiyle e-posta ve admin bayrağının değiştirilemediğini doğrular.

        Senaryo:
        - Yetkili kullanıcı profiline `email` ve `is_staff` değerleri PATCH eder.

        Beklenti:
        - İstek başarılı dönse de e-posta ve admin bayrağı değişmemelidir.
        """
        self.client.force_authenticate(self.user)

        self.client.patch(reverse('accounts:me'), {'email': 'yeni@example.com', 'is_staff': True}, format='json')

        self.user.refresh_from_db()
        self.assertEqual(self.user.email, 'ayse@example.com')
        self.assertFalse(self.user.is_staff)

    def test_password_is_stored_hashed(self):
        """Parolanın veritabanında düz metin olarak saklanmadığını doğrular."""
        self.assertNotEqual(self.user.password, PASSWORD)
        self.assertTrue(self.user.password.startswith(('pbkdf2_', 'argon2', 'bcrypt')))

    def test_login_is_throttled(self):
        """
        Giriş endpoint'inin IP bazında hız sınırına takıldığını doğrular (kaba kuvvet koruması).

        Senaryo:
        - Giriş oranı dakikada 1 olarak ayarlanır ve iki istek gönderilir.

        Beklenti:
        - İlk istek işlenmeli, ikinci istek 429 dönmelidir.
        """
        url = reverse('accounts:token')
        data = {'email': 'ayse@example.com', 'password': 'yanlis'}
        with patch.dict(SimpleRateThrottle.THROTTLE_RATES, {LoginRateThrottle.scope: '1/minute'}):
            first = self.client.post(url, data, format='json')
            second = self.client.post(url, data, format='json')

        self.assertEqual(first.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(second.status_code, status.HTTP_429_TOO_MANY_REQUESTS)

    def test_register_is_throttled_independently(self):
        """
        Kayıt hız sınırının giriş kotasından bağımsız işlediğini doğrular.

        Senaryo:
        - Kayıt oranı dakikada 1 yapılır, iki kayıt denenir.
        - Ardından giriş endpoint'i çağrılır.

        Beklenti:
        - İkinci kayıt 429 dönmeli, giriş isteği throttle'a takılmamalıdır.
        """
        url = reverse('accounts:register')
        with patch.dict(SimpleRateThrottle.THROTTLE_RATES, {RegisterRateThrottle.scope: '1/minute'}):
            self.client.post(url, {}, format='json')
            second = self.client.post(url, {}, format='json')
            login = self.client.post(
                reverse('accounts:token'), {'email': 'ayse@example.com', 'password': PASSWORD}, format='json',
            )

        self.assertEqual(second.status_code, status.HTTP_429_TOO_MANY_REQUESTS)
        self.assertEqual(login.status_code, status.HTTP_200_OK)
