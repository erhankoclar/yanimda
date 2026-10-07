from django.contrib.auth import get_user_model
from django.test import TestCase

User = get_user_model()


class UserManagerTests(TestCase):
    def test_create_user_uses_email_as_username(self):
        """
        Standart kullanıcının e-posta ile oluşturulduğunu doğrular.

        Senaryo:
        - Büyük harf içeren bir e-posta ve parola ile kullanıcı oluşturulur.

        Beklenti:
        - E-posta küçük harfe çevrilmiş olmalı, parola doğrulanmalı.
        - Kullanıcı admin yetkisine sahip olmamalıdır.
        """
        user = User.objects.create_user(email='Ayse@Example.com', password='guclu-parola-123')

        self.assertEqual(user.email, 'ayse@example.com')
        self.assertTrue(user.check_password('guclu-parola-123'))
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)

    def test_create_user_without_email_raises(self):
        """E-posta verilmeden kullanıcı oluşturma girişiminin hata verdiğini doğrular (hata yolu)."""
        with self.assertRaises(ValueError):
            User.objects.create_user(email='', password='guclu-parola-123')

    def test_create_superuser_sets_admin_flags(self):
        """
        Süper kullanıcının admin bayraklarıyla oluşturulduğunu doğrular.

        Senaryo:
        - create_superuser ile kullanıcı oluşturulur.

        Beklenti:
        - is_staff ve is_superuser True olmalıdır.
        """
        user = User.objects.create_superuser(email='admin@example.com', password='guclu-parola-123')

        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)

    def test_str_prefers_full_name(self):
        """
        Metin temsilinin ad soyadı, yoksa e-postayı kullandığını doğrular.

        Senaryo:
        - Biri adlı, biri adsız iki kullanıcı oluşturulur.

        Beklenti:
        - Adlı kullanıcıda ad soyad, adsız kullanıcıda e-posta dönmelidir.
        """
        named = User.objects.create_user(email='a@example.com', first_name='Ayşe', last_name='Yılmaz')
        unnamed = User.objects.create_user(email='b@example.com')

        self.assertEqual(str(named), 'Ayşe Yılmaz')
        self.assertEqual(str(unnamed), 'b@example.com')
