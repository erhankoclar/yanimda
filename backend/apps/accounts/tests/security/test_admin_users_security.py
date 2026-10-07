from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from apps.care.tests.factories import make_user


class AdminUserSecurityTests(APITestCase):
    def setUp(self):
        """Hedef kullanıcıyı ve admin kullanıcı adreslerini hazırlar."""
        self.target = make_user()
        self.urls = [
            reverse('accounts-admin:user-list'),
            reverse('accounts-admin:user-detail', args=[self.target.pk]),
        ]

    def test_anonymous_and_applicant_are_rejected(self):
        """
        Kullanıcı yönetimi adreslerine yalnızca adminlerin erişebildiğini doğrular.

        Senaryo:
        - Adresler önce kimliksiz, sonra standart kullanıcıyla çağrılır.

        Beklenti:
        - Kimliksiz istekler 401, standart kullanıcı istekleri 403 dönmelidir.
        """
        for url in self.urls:
            with self.subTest(url=url):
                self.assertEqual(self.client.get(url).status_code, status.HTTP_401_UNAUTHORIZED)

        self.client.force_authenticate(make_user())
        for url in self.urls:
            with self.subTest(url=url):
                self.assertEqual(self.client.get(url).status_code, status.HTTP_403_FORBIDDEN)

    def test_password_hash_is_never_exposed(self):
        """Kullanıcı listesi ve detayında parola özetinin yer almadığını doğrular (hassas veri sızıntısı)."""
        self.client.force_authenticate(make_user(is_staff=True))

        listing = self.client.get(self.urls[0]).data['results'][0]
        detail = self.client.get(self.urls[1]).data

        for data in (listing, detail):
            self.assertNotIn('password', data)
            self.assertNotIn(self.target.password, str(data))

    def test_user_endpoints_are_read_only(self):
        """
        Admin kullanıcı detayında değiştirme ve silme metotlarının kapalı olduğunu doğrular.

        Senaryo:
        - Admin, kullanıcıyı admin yapmaya ve silmeye çalışır.

        Beklenti:
        - İstekler 405 dönmeli; kullanıcı yetkisiz ve kayıtlı kalmalıdır.
        """
        self.client.force_authenticate(make_user(is_staff=True))

        self.assertEqual(self.client.patch(self.urls[1], {'is_staff': True}).status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        self.assertEqual(self.client.delete(self.urls[1]).status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        self.target.refresh_from_db()
        self.assertFalse(self.target.is_staff)
