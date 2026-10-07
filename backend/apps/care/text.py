"""Metin karşılaştırma yardımcıları."""

import re

# Türkçede I/İ/ı/i farklı harflerdir ama kullanıcılar büyük harfle veya
# Türkçe klavye olmadan yazınca birbirinin yerine geçer; karşılaştırmada tek harfe indirilir.
_TURKISH_I_VARIANTS = str.maketrans({'I': 'i', 'İ': 'i', 'ı': 'i'})


def person_name_key(value):
    """
    Kişi adını büyük/küçük harf, Türkçe i varyantları ve boşluklardan bağımsız karşılaştırma anahtarına çevirir.

    Örneğin "FATMA YILMAZ", "fatma  yılmaz" ve "Fatma Yilmaz" aynı anahtarı üretir.

    Args:
        value (str): Kişinin adı soyadı.

    Returns:
        str: Karşılaştırma anahtarı.
    """
    folded = value.translate(_TURKISH_I_VARIANTS).casefold()
    return re.sub(r'\s+', ' ', folded).strip()
