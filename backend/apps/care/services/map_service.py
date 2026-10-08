"""Admin tematik haritası için ilçe ve mahalle bazında talep sayıları."""

from datetime import timedelta

from django.db.models import Count
from django.utils import timezone

from apps.care.models import CareRequest, ServiceInquiry, ServiceType
from apps.care.services.service_type_service import localized
from apps.geo.models import District, Neighborhood

SOURCES = ('all', 'inquiries', 'requests')


def _counts(queryset):
    """
    Kayıtları mahalle ve hizmete göre veritabanında sayar; konumu olmayan kayıtlar atlanır.

    Args:
        queryset (QuerySet): Başvuru veya hızlı talep sorgusu.

    Returns:
        list[tuple[int, int, int]]: (mahalle kimliği, hizmet kimliği, sayı) üçlüleri.
    """
    return list(
        queryset.filter(neighborhood__isnull=False)
        .values_list('neighborhood_id', 'service_id')
        .annotate(count=Count('id'))
        .order_by()
    )


def _add(target, service_id, count):
    """
    Bir alanın toplamına ve hizmet dağılımına sayı ekler.

    Args:
        target (dict): `count` ve `by_service` alanlı sayaç.
        service_id (int): Hizmet kimliği.
        count (int): Eklenecek sayı.
    """
    target['count'] += count
    key = str(service_id)
    target['by_service'][key] = target['by_service'].get(key, 0) + count


def build_map(source='all', days=None, today=None):
    """
    Haritanın ilçe ve mahalle katmanları için toplam ve hizmet bazında sayıları hesaplar.

    Sayımlar veritabanında gruplandığı için sorgu sayısı kayıt sayısından bağımsızdır.
    Sayısı sıfır olan mahalleler yanıta konmaz; ilçelerin hepsi döner.

    Args:
        source (str): `all`, `inquiries` veya `requests`.
        days (Optional[int]): Yalnızca son bu kadar gün; None ise tüm kayıtlar.
        today (Optional[date]): Bugünün tarihi; testler için verilebilir.

    Returns:
        dict[str, Any]: `total`, `services`, `districts` ve `neighborhoods` alanlı sözlük.
    """
    querysets = {'inquiries': ServiceInquiry.objects.all(), 'requests': CareRequest.objects.all()}
    if days:
        first_day = (today or timezone.localdate()) - timedelta(days=days - 1)
        querysets = {name: queryset.filter(created_at__date__gte=first_day) for name, queryset in querysets.items()}
    rows = []
    for name, queryset in querysets.items():
        if source in ('all', name):
            rows.extend(_counts(queryset))

    # Kaydı olan mahallelerin adı, harita kimliği ve ilçesi tek sorguda okunur.
    places = {
        place['id']: {**place, 'count': 0, 'by_service': {}}
        for place in Neighborhood.objects.filter(id__in={row[0] for row in rows}).values('id', 'osm_id', 'name', 'district_id')
    }
    districts = {
        district.id: {'id': district.id, 'osm_id': district.osm_id, 'name': district.name, 'count': 0, 'by_service': {}}
        for district in District.objects.ordered()
    }
    services = {}
    total = 0
    for neighborhood_id, service_id, count in rows:
        total += count
        services[service_id] = services.get(service_id, 0) + count
        place = places[neighborhood_id]
        _add(place, service_id, count)
        _add(districts[place['district_id']], service_id, count)

    return {
        'total': total,
        'services': [
            {'id': service.id, 'name': localized(service, 'name'), 'icon': service.icon, 'count': services.get(service.id, 0)}
            for service in ServiceType.objects.active()
        ],
        'districts': list(districts.values()),
        'neighborhoods': sorted(places.values(), key=lambda item: -item['count']),
    }
