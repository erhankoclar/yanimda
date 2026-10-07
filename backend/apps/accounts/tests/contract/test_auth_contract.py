from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.urls import reverse
from rest_framework.test import APITestCase

User = get_user_model()

PASSWORD = 'Yanimda-Guclu-2026'


class AuthResponseContractTests(APITestCase):
    """Frontend'in auth store'unun bağlı olduğu yanıt alanlarını sabitler."""

    def setUp(self):
        """Throttle sayaçlarını sıfırlar ve kullanıcı oluşturur."""
        cache.clear()
        self.user = User.objects.create_user(email='ayse@example.com', password=PASSWORD, first_name='Ayşe')

    def test_token_response_fields(self):
        """
        Giriş yanıtının yalnızca `access` ve `refresh` alanlarını içerdiğini doğrular.

        Senaryo:
        - Geçerli bilgilerle token alınır.

        Beklenti:
        - Alan kümesi tam olarak {access, refresh} olmalı ve değerler metin olmalıdır.
        """
        data = self.client.post(
            reverse('accounts:token'), {'email': 'ayse@example.com', 'password': PASSWORD}, format='json',
        ).data

        self.assertEqual(set(data), {'access', 'refresh'})
        self.assertIsInstance(data['access'], str)

    def test_me_response_fields(self):
        """
        Profil yanıtının alan kümesini ve tiplerini doğrular.

        Senaryo:
        - Yetkili kullanıcı profil endpoint'ini çağırır.

        Beklenti:
        - Alan kümesi sabit olmalı; `id` sayı, `is_staff` mantıksal olmalıdır.
        """
        self.client.force_authenticate(self.user)

        data = self.client.get(reverse('accounts:me')).data

        self.assertEqual(set(data), {'id', 'email', 'first_name', 'last_name', 'phone', 'is_staff'})
        self.assertIsInstance(data['id'], int)
        self.assertIsInstance(data['is_staff'], bool)

    def test_register_response_fields(self):
        """Kayıt yanıtının parolayı içermeyen sabit alan kümesini doğrular."""
        data = self.client.post(reverse('accounts:register'), {
            'email': 'yeni@example.com', 'password': PASSWORD, 'first_name': 'Yeni', 'last_name': 'Kişi',
        }, format='json').data

        self.assertEqual(set(data), {'id', 'email', 'first_name', 'last_name', 'phone'})


class AdminUserContractTests(APITestCase):
    def test_admin_user_row_fields(self):
        """
        Admin kullanıcı satırı ve detayının alan kümesini doğrular.

        Senaryo:
        - Admin oturumuyla kullanıcı listesi ve detayı çağrılır.

        Beklenti:
        - Her ikisi de aynı sabit alan kümesine sahip olmalıdır.
        """
        admin = User.objects.create_user(email='admin@example.com', password=PASSWORD, is_staff=True)
        self.client.force_authenticate(admin)
        expected = {
            'id', 'email', 'first_name', 'last_name', 'full_name', 'phone',
            'is_staff', 'is_active', 'date_joined', 'last_login', 'request_count',
        }

        row = self.client.get(reverse('accounts-admin:user-list')).data['results'][0]
        detail = self.client.get(reverse('accounts-admin:user-detail', args=[admin.pk])).data

        self.assertEqual(set(row), expected)
        self.assertEqual(set(detail), expected)
