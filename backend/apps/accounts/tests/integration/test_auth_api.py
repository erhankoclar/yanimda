from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.urls import reverse
from django.utils.translation import gettext
from rest_framework import status
from rest_framework.test import APITestCase

User = get_user_model()

PASSWORD = settings.TEST_USER_PASSWORD


class AuthApiTestCase(APITestCase):
    def setUp(self):
        """Throttle sayaçlarının testler arasında taşınmaması için önbelleği temizler."""
        cache.clear()

    def register(self, **overrides):
        """
        Varsayılan geçerli verilerle kayıt endpoint'ini çağırır.

        Args:
            **overrides (Any): Varsayılan kayıt alanlarını ezen değerler.

        Returns:
            Response: Kayıt endpoint'inin yanıtı.
        """
        payload = {
            'email': 'ayse@example.com',
            'password': PASSWORD,
            'first_name': 'Ayşe',
            'last_name': 'Yılmaz',
            'phone': '05551112233',
            **overrides,
        }
        return self.client.post(reverse('accounts:register'), payload, format='json')

    def login(self, email='ayse@example.com', password=PASSWORD):
        """
        Token endpoint'ine giriş isteği gönderir.

        Args:
            email (str): Giriş e-postası.
            password (str): Giriş parolası.

        Returns:
            Response: Token endpoint'inin yanıtı.
        """
        return self.client.post(reverse('accounts:token'), {'email': email, 'password': password}, format='json')


class RegisterApiTests(AuthApiTestCase):
    def test_register_creates_applicant(self):
        """
        Geçerli verilerle kaydın başvuru sahibi hesabı oluşturduğunu doğrular.

        Senaryo:
        - Kayıt endpoint'i geçerli verilerle çağrılır.

        Beklenti:
        - 201 dönmeli, yanıtta parola bulunmamalıdır.
        - Kullanıcı veritabanında admin yetkisi olmadan oluşmalıdır.
        """
        response = self.register()

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['email'], 'ayse@example.com')
        self.assertNotIn('password', response.data)
        user = User.objects.get(email='ayse@example.com')
        self.assertEqual(user.phone, '05551112233')
        self.assertFalse(user.is_staff)

    def test_register_rejects_duplicate_email_case_insensitively(self):
        """
        Aynı e-postanın farklı harf büyüklüğüyle tekrar kaydedilemediğini doğrular (hata yolu).

        Senaryo:
        - Bir hesap oluşturulur.
        - Aynı e-posta büyük harflerle tekrar kaydedilmeye çalışılır.

        Beklenti:
        - 400 dönmeli ve e-posta alanında çevrilmiş tekrar hatası bulunmalıdır.
        """
        self.register()

        response = self.register(email='AYSE@example.com')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['email'], [gettext('A user with this email address already exists.')])

    def test_register_rejects_weak_password(self):
        """
        Parola kurallarına uymayan parolanın reddedildiğini doğrular (hata yolu).

        Senaryo:
        - Kayıt yalnızca rakamlardan oluşan kısa bir parola ile denenir.

        Beklenti:
        - 400 dönmeli, hata `password` alanında olmalı ve kullanıcı oluşmamalıdır.
        """
        response = self.register(password='1234')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('password', response.data)
        self.assertFalse(User.objects.exists())

    def test_register_requires_names(self):
        """Ad ve soyad gönderilmeden kayıt yapılamadığını doğrular (hata yolu)."""
        response = self.register(first_name='', last_name='')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('first_name', response.data)
        self.assertIn('last_name', response.data)


class TokenApiTests(AuthApiTestCase):
    def setUp(self):
        """Giriş testleri için kayıtlı bir kullanıcı hazırlar."""
        super().setUp()
        self.register()

    def test_login_returns_token_pair(self):
        """
        Doğru bilgilerle girişte access ve refresh token döndüğünü doğrular.

        Senaryo:
        - Kayıtlı kullanıcı doğru parola ile giriş yapar.

        Beklenti:
        - 200 dönmeli ve yanıtta `access` ile `refresh` bulunmalıdır.
        """
        response = self.login()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

    def test_refresh_returns_new_access_token(self):
        """
        Refresh token ile yeni access token alınabildiğini doğrular.

        Senaryo:
        - Giriş yapılır ve dönen refresh token ile yenileme endpoint'i çağrılır.

        Beklenti:
        - 200 dönmeli; yeni `access` ve döndürülmüş yeni `refresh` bulunmalıdır.
        """
        refresh = self.login().data['refresh']

        response = self.client.post(reverse('accounts:token-refresh'), {'refresh': refresh}, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertNotEqual(response.data['refresh'], refresh)


class MeApiTests(AuthApiTestCase):
    def setUp(self):
        """Profil testleri için kayıtlı ve token ile yetkilendirilmiş istemci hazırlar."""
        super().setUp()
        self.register()
        access = self.login().data['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access}')

    def test_me_returns_current_user(self):
        """
        Profil endpoint'inin token sahibinin bilgilerini döndürdüğünü doğrular.

        Senaryo:
        - Yetkili istemciyle profil endpoint'i çağrılır.

        Beklenti:
        - 200 dönmeli; e-posta, ad ve admin bayrağı doğru olmalıdır.
        """
        response = self.client.get(reverse('accounts:me'))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['email'], 'ayse@example.com')
        self.assertEqual(response.data['first_name'], 'Ayşe')
        self.assertFalse(response.data['is_staff'])

    def test_me_patch_updates_profile_fields(self):
        """
        Profilde ad ve telefonun güncellenebildiğini doğrular.

        Senaryo:
        - Profil endpoint'ine yeni ad ve telefon PATCH edilir.

        Beklenti:
        - 200 dönmeli ve değerler veritabanına yazılmalıdır.
        """
        response = self.client.patch(reverse('accounts:me'), {'first_name': 'Ayşegül', 'phone': '05559998877'})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        user = User.objects.get(email='ayse@example.com')
        self.assertEqual(user.first_name, 'Ayşegül')
        self.assertEqual(user.phone, '05559998877')

    def test_me_put_is_not_allowed(self):
        """Profilin yalnızca PATCH ile güncellenebildiğini, PUT'un kapalı olduğunu doğrular."""
        response = self.client.put(reverse('accounts:me'), {'first_name': 'X'})

        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
