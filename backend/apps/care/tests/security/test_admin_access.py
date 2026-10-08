from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from apps.care.tests.factories import make_care_request, make_user


class AdminEndpointAccessTests(APITestCase):
    """Admin endpoint'lerinin yalnızca `is_staff` kullanıcılara açık olduğunu doğrular."""

    def admin_urls(self):
        """
        Erişim kuralları sınanacak admin adreslerini döndürür.

        Returns:
            list[str]: Admin endpoint adresleri.
        """
        care_request = make_care_request()
        return [
            reverse('care-admin:dashboard'),
            reverse('care-admin:stats'),
            reverse('care-admin:request-list'),
            reverse('care-admin:request-detail', args=[care_request.pk]),
        ]

    def test_anonymous_gets_401(self):
        """Kimlik doğrulaması olmadan admin endpoint'lerine erişilemediğini doğrular."""
        for url in self.admin_urls():
            with self.subTest(url=url):
                self.assertEqual(self.client.get(url).status_code, status.HTTP_401_UNAUTHORIZED)

    def test_applicant_gets_403(self):
        """
        Standart başvuru sahibinin admin endpoint'lerine erişemediğini doğrular (yetki kontrolü).

        Senaryo:
        - Kendi talebi olan standart kullanıcı oturum açar ve admin adreslerini çağırır.

        Beklenti:
        - Hepsi 403 dönmeli; diğer kullanıcıların verisi görünmemelidir.
        """
        applicant = make_user()
        make_care_request(applicant=applicant)
        self.client.force_authenticate(applicant)

        for url in self.admin_urls():
            with self.subTest(url=url):
                self.assertEqual(self.client.get(url).status_code, status.HTTP_403_FORBIDDEN)

    def test_inactive_admin_is_rejected(self):
        """Pasif hale getirilmiş admin hesabının JWT ile erişemediğini doğrular."""
        admin = make_user(is_staff=True, is_active=False)
        from rest_framework_simplejwt.tokens import AccessToken

        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {AccessToken.for_user(admin)}')

        for url in self.admin_urls():
            with self.subTest(url=url):
                self.assertEqual(self.client.get(url).status_code, status.HTTP_401_UNAUTHORIZED)
