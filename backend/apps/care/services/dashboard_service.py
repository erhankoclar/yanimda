"""Admin gösterge panelinin (dashboard) okuma servisi."""

from datetime import timedelta

from django.db.models import Count, Q
from django.db.models.functions import TruncDate, TruncWeek
from django.utils import timezone

from apps.care.models import CareRequest, ServiceInquiry, ServiceType

WEEKLY_FROM_DAYS = 90
RECENT_LIMIT = 8
PENDING_LIMIT = 5


def change_percent(current, previous):
    """
    İki dönem arasındaki yüzde değişimi hesaplar.

    Args:
        current (int): Bu dönemin değeri.
        previous (int): Önceki dönemin değeri.

    Returns:
        Optional[int]: Yuvarlanmış yüzde değişim; önceki dönem 0 ise kıyas anlamsız olduğundan None.
    """
    if not previous:
        return None
    return round((current - previous) * 100 / previous)


def month_periods(today):
    """
    Bu ayın başından bugüne ve geçen ayın aynı gün aralığını döndürür.

    Geçen ay daha kısaysa aralık geçen ayın son gününde biter (ör. 31 Mart → 28 Şubat).

    Args:
        today (date): Bugünün tarihi.

    Returns:
        tuple[tuple[date, date], tuple[date, date]]: (bu ay başlangıç, bitiş), (geçen ay başlangıç, bitiş).
    """
    this_start = today.replace(day=1)
    previous_end_of_month = this_start - timedelta(days=1)
    previous_start = previous_end_of_month.replace(day=1)
    previous_end = min(previous_start + timedelta(days=today.day - 1), previous_end_of_month)
    return (this_start, today), (previous_start, previous_end)


def bucket_starts(first_day, last_day, bucket):
    """
    Grafiğin x eksenindeki gün veya hafta başlangıçlarını üretir.

    Args:
        first_day (date): Aralığın ilk günü.
        last_day (date): Aralığın son günü.
        bucket (str): `day` veya `week`; haftalar pazartesi başlar.

    Returns:
        list[date]: Sıralı dönem başlangıçları.
    """
    if bucket == 'week':
        current = first_day - timedelta(days=first_day.weekday())
        step = timedelta(days=7)
    else:
        current = first_day
        step = timedelta(days=1)
    starts = []
    while current <= last_day:
        starts.append(current)
        current += step
    return starts


def _counts_by_service_and_bucket(queryset, bucket):
    """
    Kayıtları hizmet ve dönem (gün/hafta) başına sayar.

    Args:
        queryset (QuerySet): Tarihle daraltılmış hızlı talep veya başvuru sorgusu.
        bucket (str): `day` veya `week`.

    Returns:
        dict[tuple[int, date], int]: (hizmet kimliği, dönem başlangıcı) → kayıt sayısı.
    """
    trunc = TruncWeek('created_at') if bucket == 'week' else TruncDate('created_at')
    rows = queryset.annotate(period=trunc).values_list('service_id', 'period').annotate(count=Count('id'))
    counts = {}
    for service_id, period, count in rows:
        key = (service_id, period.date() if hasattr(period, 'date') else period)
        counts[key] = counts.get(key, 0) + count
    return counts


def _series(days, source, today, services):
    """
    Her aktif hizmet için seçilen kaynaktaki kayıt sayılarının zaman serisini üretir.

    Args:
        days (int): Geriye doğru gün sayısı (7, 30 veya 90).
        source (str): `all`, `inquiries` veya `requests`.
        today (date): Bugünün tarihi.
        services (list[ServiceType]): Aktif hizmetler, gösterim sırasıyla.

    Returns:
        dict[str, Any]: `bucket`, `labels` ve hizmet başına `datasets`.
    """
    bucket = 'week' if days >= WEEKLY_FROM_DAYS else 'day'
    first_day = today - timedelta(days=days - 1)
    starts = bucket_starts(first_day, today, bucket)
    managers = {'inquiries': ServiceInquiry.objects, 'requests': CareRequest.objects}
    counts = {}
    for name, manager in managers.items():
        if source in ('all', name):
            for key, value in _counts_by_service_and_bucket(manager.created_on_or_after(first_day), bucket).items():
                counts[key] = counts.get(key, 0) + value
    return {
        'bucket': bucket,
        'labels': starts,
        'datasets': [
            {
                'service_id': service.id,
                'name': service.name,
                'icon': service.icon,
                'counts': [counts.get((service.id, start), 0) for start in starts],
            }
            for service in services
        ],
    }


def _recent(limit):
    """
    Son gelen hızlı talepleri ve başvuruları zamana göre birleştirir.

    Args:
        limit (int): Döndürülecek kayıt sayısı.

    Returns:
        list[dict[str, Any]]: En yeniden eskiye kayıtlar.
    """
    items = [
        {'type': 'inquiry', 'id': item.id, 'title': item.full_name, 'service': item.service,
         'created_at': item.created_at, 'status': None}
        for item in ServiceInquiry.objects.latest_first()[:limit]
    ] + [
        {'type': 'request', 'id': item.id, 'title': item.elder_full_name, 'service': item.service,
         'created_at': item.created_at, 'status': item.status}
        for item in CareRequest.objects.latest_first()[:limit]
    ]
    items.sort(key=lambda item: item['created_at'], reverse=True)
    return items[:limit]


def build_dashboard(days=30, source='all', today=None):
    """
    Gösterge panelinin kartlarını, hizmet serisini, son kayıtlarını ve bekleyen işlerini hesaplar.

    Sorgu sayısı kayıt sayısından bağımsızdır; tüm sayımlar veritabanında toplanır.

    Args:
        days (int): Grafik için geriye doğru gün sayısı (7, 30 veya 90).
        source (str): Grafikte sayılacak kaynak: `all`, `inquiries` veya `requests`.
        today (Optional[date]): Bugünün tarihi; testler için verilebilir.

    Returns:
        dict[str, Any]: `cards`, `series`, `recent`, `pending` ve `status_breakdown` anahtarlarını içeren sözlük.
    """
    today = today or timezone.localdate()
    (this_start, this_end), (previous_start, previous_end) = month_periods(today)
    in_this = Q(created_at__date__gte=this_start, created_at__date__lte=this_end)
    in_previous = Q(created_at__date__gte=previous_start, created_at__date__lte=previous_end)

    inquiry_totals = ServiceInquiry.objects.aggregate(
        this=Count('id', filter=in_this), previous=Count('id', filter=in_previous),
    )
    request_totals = CareRequest.objects.aggregate(
        this=Count('id', filter=in_this),
        previous=Count('id', filter=in_previous),
        open=Count('id', filter=Q(status__in=CareRequest.OPEN_STATUSES)),
        new=Count('id', filter=Q(status=CareRequest.Status.NEW)),
    )
    services = list(ServiceType.objects.active().with_demand())
    top_service = max(services, key=lambda service: service.demand, default=None)
    status_counts = dict(CareRequest.objects.values_list('status').annotate(count=Count('id')))
    pending = list(CareRequest.objects.waiting_for_review()[:PENDING_LIMIT])

    demand_this = inquiry_totals['this'] + request_totals['this']
    demand_previous = inquiry_totals['previous'] + request_totals['previous']
    return {
        'cards': {
            'total_demand': {
                'value': demand_this, 'previous': demand_previous,
                'change_percent': change_percent(demand_this, demand_previous),
            },
            'open_requests': {'value': request_totals['open'], 'new': request_totals['new']},
            'inquiries': {
                'value': inquiry_totals['this'], 'previous': inquiry_totals['previous'],
                'change_percent': change_percent(inquiry_totals['this'], inquiry_totals['previous']),
            },
            'services': {
                'value': len(services),
                'top_service': top_service.name if top_service and top_service.demand else None,
            },
        },
        'series': _series(days, source, today, services),
        'recent': _recent(RECENT_LIMIT),
        'pending': pending,
        'status_breakdown': [
            {'status': value, 'label': label, 'count': status_counts.get(value, 0)}
            for value, label in CareRequest.Status.choices
        ],
    }
