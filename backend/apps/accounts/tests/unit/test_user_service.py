from django.contrib.auth import get_user_model
from django.test import TestCase

from apps.accounts.services import user_service

User = get_user_model()


class UserServiceTests(TestCase):
    def test_register_applicant_creates_non_admin_with_hashed_password(self):
        """
        Kayıt servisinin admin yetkisi olmayan, parolası özetlenmiş hesap açtığını doğrular.

        Senaryo:
        - Büyük harfli e-postayla başvuru sahibi kaydedilir.

        Beklenti:
        - E-posta küçük harfle saklanmalı, parola doğrulanmalı, yetki bayrakları kapalı olmalıdır.
        """
        user = user_service.register_applicant(
            email='Ayse@Example.com', password='Kurgusal-Parola-2026', first_name='Ayşe', last_name='Yılmaz',
        )

        self.assertEqual(user.email, 'ayse@example.com')
        self.assertTrue(user.check_password('Kurgusal-Parola-2026'))
        self.assertFalse(user.is_staff or user.is_superuser)

    def test_update_profile_changes_only_allowed_fields(self):
        """
        Profil güncellemesinin yalnızca ad, soyad ve telefonu değiştirdiğini doğrular.

        Senaryo:
        - Servise ad ile birlikte e-posta ve admin bayrağı gönderilir.

        Beklenti:
        - Ad değişmeli; e-posta ve admin bayrağı değişmemelidir.
        """
        user = User.objects.create_user(email='a@example.com', password='x')

        user_service.update_profile(user, first_name='Yeni', email='b@example.com', is_staff=True)

        user.refresh_from_db()
        self.assertEqual(user.first_name, 'Yeni')
        self.assertEqual(user.email, 'a@example.com')
        self.assertFalse(user.is_staff)

    def test_email_is_registered_ignores_case_and_spaces(self):
        """E-posta kayıt kontrolünün büyük/küçük harf ve boşluklardan bağımsız olduğunu doğrular."""
        User.objects.create_user(email='a@example.com')

        self.assertTrue(user_service.email_is_registered('  A@EXAMPLE.com '))
        self.assertFalse(user_service.email_is_registered('b@example.com'))

    def test_manager_hooks_delegate_to_the_service(self):
        """Django'nun manager kancalarının (createsuperuser) servis kurallarıyla çalıştığını doğrular."""
        admin = User.objects.create_superuser(email='Admin@Example.com', password='x')

        self.assertEqual(admin.email, 'admin@example.com')
        self.assertTrue(admin.is_staff and admin.is_superuser)
        with self.assertRaises(ValueError):
            User.objects.create_superuser(email='b@example.com', password='x', is_staff=False)
