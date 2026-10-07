import re

from django.utils.translation import gettext
from rest_framework import serializers

_PHONE_ALLOWED = re.compile(r'^\+?[\d\s()-]+$')


def normalize_phone(value):
    """
    Telefon numarasını doğrular ve boşluk/ayraçlardan arındırır.

    Args:
        value (str): Kullanıcının girdiği telefon numarası.

    Returns:
        str: Yalnızca rakam ve isteğe bağlı baştaki `+` işaretinden oluşan numara.

    Raises:
        serializers.ValidationError: Geçersiz karakter içeriyorsa veya rakam sayısı 10-15 aralığında değilse.
    """
    value = value.strip()
    digits = re.sub(r'\D', '', value)
    if not _PHONE_ALLOWED.match(value) or not 10 <= len(digits) <= 15:
        raise serializers.ValidationError(gettext('Enter a valid phone number.'))
    return ('+' if value.startswith('+') else '') + digits
