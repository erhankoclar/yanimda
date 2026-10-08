from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from apps.care.tests.factories import make_user


class AdminMapAccessTests(APITestCase):
    """Harita endpoint'inin yalnızca yönetici ve yalnızca okuma için açık olduğunu doğrular."""

    def setUp(self):
        """Harita adresini hazırlar."""
        self.url = reverse('care-admin:map')

    def test_anonymous_gets_401(self):
        """
        Kimliksiz isteğin reddedildiğini doğrular.

        Senaryo:
        - Oturum açmadan GET yapılır.

        Beklenti:
        - 401 dönmelidir.
        """
        self.assertEqual(self.client.get(self.url).status_code, status.HTTP_401_UNAUTHORIZED)

    def test_non_staff_gets_403(self):
        """
        Yönetici olmayan kullanıcının reddedildiğini doğrular.

        Senaryo:
        - Sıradan kullanıcıyla GET yapılır.

        Beklenti:
        - 403 dönmelidir.
        """
        self.client.force_authenticate(make_user())

        self.assertEqual(self.client.get(self.url).status_code, status.HTTP_403_FORBIDDEN)

    def test_only_get_allowed(self):
        """
        Yöneticinin bile yazma yöntemlerini kullanamadığını doğrular.

        Senaryo:
        - Yönetici POST, PUT, PATCH ve DELETE dener.

        Beklenti:
        - Hepsi 405 dönmelidir.
        """
        self.client.force_authenticate(make_user(is_staff=True))

        for method in ('post', 'put', 'patch', 'delete'):
            with self.subTest(method=method):
                response = getattr(self.client, method)(self.url, {})

                self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
