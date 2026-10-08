from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

User = get_user_model()

PASSWORD = settings.TEST_USER_PASSWORD


class EmailCaseLoginTests(APITestCase):
    def setUp(self):
        """Throttle sayaçlarını sıfırlar ve küçük harfli e-postayla kullanıcı oluşturur."""
        cache.clear()
        User.objects.create_user(email='ayse@example.com', password=PASSWORD)

    def test_login_accepts_email_in_different_case(self):
        """
        E-postanın farklı harf büyüklüğüyle yazılması durumunda girişin çalıştığını doğrular.

        Senaryo:
        - Kayıt e-postayı küçük harfle saklar.
        - Kullanıcı girişte e-postasını büyük harflerle yazar.

        Beklenti:
        - 200 dönmeli ve token verilmelidir; daha önce bu durumda 401 dönüyordu.
        """
        response = self.client.post(
            reverse('accounts:token'), {'email': ' AYSE@Example.com ', 'password': PASSWORD}, format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)

    def test_lookup_by_natural_key_ignores_case(self):
        """Kullanıcının e-posta doğal anahtarıyla büyük/küçük harf duyarsız bulunduğunu doğrular."""
        self.assertEqual(User.objects.get_by_natural_key('Ayse@EXAMPLE.com').email, 'ayse@example.com')
