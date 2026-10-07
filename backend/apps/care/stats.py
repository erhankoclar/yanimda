"""Admin dashboard istatistiklerinin hesaplanması."""

from datetime import timedelta

from django.contrib.auth import get_user_model
from django.db.models import Count, Q
from django.db.models.functions import TruncDate
from django.utils import timezone

from apps.care.models import CareRequest, ServiceType

DAILY_SERIES_DAYS = 14
RECENT_DAYS = 7
OPEN_STATUSES = [CareRequest.Status.NEW, CareRequest.Status.REVIEWING, CareRequest.Status.ASSIGNED]


def build_dashboard_stats():
    """
    Admin dashboard'unda gösterilen özet sayıları ve dağılımları hesaplar.

    Sorgu sayısı kayıt sayısından bağımsızdır; tüm sayımlar veritabanında
    toplanır.

    Returns:
        dict[str, Any]: `total_requests`, `open_requests`, `requests_last_7_days`,
        `total_applicants`, `by_status`, `by_service` ve `daily` anahtarlarını içeren sözlük.
    """
    today = timezone.localdate()
    now = timezone.now()
    totals = CareRequest.objects.aggregate(
        total=Count('id'),
        open=Count('id', filter=Q(status__in=OPEN_STATUSES)),
        recent=Count('id', filter=Q(created_at__gte=now - timedelta(days=RECENT_DAYS))),
    )
    status_counts = dict(CareRequest.objects.values_list('status').annotate(count=Count('id')))
    services = ServiceType.objects.annotate(request_count=Count('requests')).order_by('sort_order', 'name')
    first_day = today - timedelta(days=DAILY_SERIES_DAYS - 1)
    daily_counts = dict(
        CareRequest.objects.filter(created_at__date__gte=first_day)
        .annotate(day=TruncDate('created_at'))
        .values_list('day')
        .annotate(count=Count('id')),
    )
    applicants = get_user_model().objects.filter(is_staff=False, is_active=True).count()

    return {
        'total_requests': totals['total'],
        'open_requests': totals['open'],
        'requests_last_7_days': totals['recent'],
        'total_applicants': applicants,
        'by_status': [
            {'status': value, 'label': label, 'count': status_counts.get(value, 0)}
            for value, label in CareRequest.Status.choices
        ],
        'by_service': [
            {'service_id': service.id, 'name': service.name, 'count': service.request_count}
            for service in services
        ],
        'daily': [
            {'date': day, 'count': daily_counts.get(day, 0)}
            for day in (first_day + timedelta(days=offset) for offset in range(DAILY_SERIES_DAYS))
        ],
    }
