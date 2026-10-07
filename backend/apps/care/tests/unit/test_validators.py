from django.test import SimpleTestCase
from rest_framework import serializers

from apps.care.validators import normalize_phone


class NormalizePhoneTests(SimpleTestCase):
    def test_strips_separators(self):
        """
        Telefondaki boşluk, parantez ve tirelerin temizlendiğini doğrular.

        Senaryo:
        - Farklı biçimlerde yazılmış telefonlar normalleştirilir.

        Beklenti:
        - Yalnızca rakamlar ve varsa baştaki `+` kalmalıdır.
        """
        self.assertEqual(normalize_phone(' 0 (555) 111-22-33 '), '05551112233')
        self.assertEqual(normalize_phone('+90 555 111 22 33'), '+905551112233')

    def test_rejects_invalid_values(self):
        """
        Geçersiz karakterli veya hatalı uzunluktaki telefonların reddedildiğini doğrular (hata yolu).

        Senaryo:
        - Harf içeren, 9 haneli ve 16 haneli değerler denenir.

        Beklenti:
        - Her biri ValidationError fırlatmalıdır.
        """
        for value in ('0555-ABC-1122', '055511122', '1234567890123456', '05551112233+'):
            with self.subTest(value=value), self.assertRaises(serializers.ValidationError):
                normalize_phone(value)
