"""İlçe ve mahalleler için veri yükleme ve okuma servisleri."""

import json
import pathlib

from django.db import transaction

from apps.geo.models import District, Neighborhood

DATA_FILE = pathlib.Path(__file__).resolve().parent.parent / 'data' / 'istanbul.json'

# Türkçe alfabe; veritabanı harmanlamasından bağımsız, doğru sıralama için kullanılır.
TURKISH_ALPHABET = 'abcçdefgğhıijklmnoöprsştuüvyz'
_ORDER = {letter: index for index, letter in enumerate(TURKISH_ALPHABET)}


def turkish_sort_key(text):
    """
    Metni Türkçe alfabe sırasına göre karşılaştırılabilir anahtara çevirir.

    Args:
        text (str): Ad.

    Returns:
        tuple[int, ...]: Harf sıraları; alfabede olmayan karakterler sona atılır.
    """
    lowered = text.replace('I', 'ı').replace('İ', 'i').lower()
    return tuple(_ORDER.get(character, len(_ORDER) + ord(character)) for character in lowered)


def list_districts():
    """
    Form seçimleri için ilçeleri Türkçe alfabe sırasıyla döndürür.

    Returns:
        QuerySet[District]: İlçeler.
    """
    return District.objects.ordered()


def list_neighborhoods(district_id):
    """
    Bir ilçenin mahallelerini Türkçe alfabe sırasıyla döndürür.

    Args:
        district_id (int): İlçe kimliği.

    Returns:
        QuerySet[Neighborhood]: Mahalleler.
    """
    return Neighborhood.objects.in_district(district_id)


def load_location_data(path=DATA_FILE):
    """
    İlçe ve mahalle ad ağacını JSON dosyasından okur.

    Args:
        path (pathlib.Path): Veri dosyası.

    Returns:
        list[dict]: `osm_id`, `name`, `slug` ve `neighborhoods` alanlı ilçeler.
    """
    return json.loads(path.read_text(encoding='utf-8'))['districts']


@transaction.atomic
def create_default_locations(data=None):
    """
    İlçe ve mahalleleri OSM kimliğine göre oluşturur, adı veya sırası değişmişleri günceller.

    Değeri aynı olan kayıtlara dokunulmaz; bu nedenle tekrar çalıştırılabilir.

    Args:
        data (Optional[list[dict]]): İlçe ağacı; verilmezse paketteki veri dosyası okunur.

    Returns:
        dict[str, int]: `created` ve `updated` kayıt sayıları.
    """
    data = data if data is not None else load_location_data()
    counts = {'created': 0, 'updated': 0}

    def upsert(model, osm_id, fields):
        """Kaydı oluşturur veya değişen alanlarını günceller; sayaçları artırır."""
        instance, created = model.objects.get_or_create(osm_id=osm_id, defaults=fields)
        if created:
            counts['created'] += 1
            return instance
        changed = [key for key, value in fields.items() if getattr(instance, key) != value]
        if changed:
            for key in changed:
                setattr(instance, key, fields[key])
            instance.save(update_fields=changed)
            counts['updated'] += 1
        return instance

    districts = sorted(data, key=lambda item: turkish_sort_key(item['name']))
    for district_order, item in enumerate(districts, start=1):
        district = upsert(District, item['osm_id'], {
            'name': item['name'], 'slug': item['slug'], 'sort_order': district_order,
        })
        neighborhoods = sorted(item['neighborhoods'], key=lambda entry: turkish_sort_key(entry['name']))
        for neighborhood_order, entry in enumerate(neighborhoods, start=1):
            upsert(Neighborhood, entry['osm_id'], {
                'name': entry['name'], 'district_id': district.id, 'sort_order': neighborhood_order,
            })
    return counts
