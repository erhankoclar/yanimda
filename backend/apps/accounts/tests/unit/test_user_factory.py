from django.contrib.auth import authenticate
from django.test import TestCase, override_settings

from apps.accounts.factories import UserFactory


class UserFactoryTests(TestCase):
    def test_password_is_read_from_settings_and_hashed(self):
        """
        Fabrikanın parolayı ayardan, kayıt anında okuyup özetlediğini doğrular.

        Senaryo:
        - `TEST_USER_PASSWORD` ayarı dışarıdan değiştirilir ve fabrikayla kullanıcı üretilir.

        Beklenti:
        - Parola düz metin saklanmamalı; yeni ayardaki parolayla giriş yapılabilmelidir.
        """
        with override_settings(TEST_USER_PASSWORD='Disaridan-Verilen-1'):
            user = UserFactory()

        self.assertNotEqual(user.password, 'Disaridan-Verilen-1')
        self.assertEqual(authenticate(email=user.email, password='Disaridan-Verilen-1'), user)

    def test_explicit_password_is_also_hashed(self):
        """
        Çağrıda verilen parolanın da özetlenerek yazıldığını doğrular.

        Senaryo:
        - Fabrika açık bir parolayla çağrılır.

        Beklenti:
        - Kullanıcı o parolayla doğrulanabilmelidir.
        """
        user = UserFactory(password='Acik-Parola-2')

        self.assertEqual(authenticate(email=user.email, password='Acik-Parola-2'), user)
