"""Geliştirme ortamında gösterge panelini anlamlı görmek için kurgusal demo verisi üretir."""

import random
from datetime import datetime, time, timedelta

from django.contrib.auth import get_user_model
from django.db import transaction
from django.utils import timezone

from apps.accounts.services import user_service
from apps.care.models import CareRequest, ServiceInquiry, ServiceType

# Demo kayıtları bu ayrılmış (gerçek olmayan) alan adındaki e-postalarla işaretlenir.
DEMO_EMAIL_DOMAIN = 'demo.yanimda.example'
DEMO_PASSWORD = 'Kurgusal-Demo-2026'
APPLICANT_COUNT = 12

FIRST_NAMES = ['Ayşe', 'Mehmet', 'Elif', 'Can', 'Zeynep', 'Murat', 'Selin', 'Emre', 'Deniz', 'Burak', 'Ece', 'Okan']
LAST_NAMES = ['Kurgu', 'Örnekoğlu', 'Deneme', 'Yalancı', 'Taslak', 'Hayali']
ELDER_FIRST_NAMES = ['Fatma', 'Hasan', 'Emine', 'Hüseyin', 'Hatice', 'Ali', 'Zehra', 'Osman', 'Saadet', 'İsmail']
DISTRICTS = [('İstanbul', 'Kadıköy'), ('İstanbul', 'Üsküdar'), ('Ankara', 'Çankaya'), ('İzmir', 'Karşıyaka'), ('Bursa', 'Nilüfer')]
MESSAGES = [
    'Haftada iki gün birkaç saatlik destek arıyoruz.',
    'Annem için kısa süreli yardım gerekiyor, ayrıntıları konuşmak isteriz.',
    'Babamın hastane randevularına eşlik edecek biri lazım.',
    'Pazar alışverişi ve eczane işleri için yardım istiyoruz.',
]


def demo_data_exists():
    """
    Veritabanında daha önce üretilmiş demo verisi olup olmadığını söyler.

    Returns:
        bool: Demo alan adlı kullanıcı veya hızlı talep varsa True.
    """
    suffix = f'@{DEMO_EMAIL_DOMAIN}'
    return (
        get_user_model().objects.filter(email__endswith=suffix).exists()
        or ServiceInquiry.objects.filter(email__endswith=suffix).exists()
    )


def remove_demo_data():
    """
    Demo kullanıcılarını (başvurularıyla birlikte) ve demo hızlı taleplerini siler.

    Returns:
        int: Silinen kullanıcı, başvuru ve hızlı talep satırlarının toplamı.
    """
    suffix = f'@{DEMO_EMAIL_DOMAIN}'
    inquiries, _details = ServiceInquiry.objects.filter(email__endswith=suffix).delete()
    users, _details = get_user_model().objects.filter(email__endswith=suffix).delete()
    return inquiries + users


def _moment(day, rng):
    """
    Verilen gün içinde mesai saatlerine düşen rastgele bir zaman üretir.

    Args:
        day (date): Gün.
        rng (random.Random): Tekrarlanabilir rastgele sayı üreteci.

    Returns:
        datetime: Etkin saat dilimindeki zaman.
    """
    moment = datetime.combine(day, time(hour=rng.randint(8, 21), minute=rng.randint(0, 59)))
    return timezone.make_aware(moment)


def _status_for_age(age_days, rng):
    """
    Başvurunun yaşına göre gerçekçi bir durum seçer: eskiler sonuçlanmış, yeniler açıktır.

    Args:
        age_days (int): Başvurunun kaç gün önce geldiği.
        rng (random.Random): Rastgele sayı üreteci.

    Returns:
        str: CareRequest.Status değeri.
    """
    if age_days > 20:
        return rng.choices([CareRequest.Status.COMPLETED, CareRequest.Status.CANCELLED], weights=[5, 1])[0]
    if age_days > 7:
        return rng.choice([CareRequest.Status.ASSIGNED, CareRequest.Status.COMPLETED, CareRequest.Status.REVIEWING])
    return rng.choices([CareRequest.Status.NEW, CareRequest.Status.REVIEWING], weights=[2, 1])[0]


def _create_applicants():
    """
    Kurgusal başvuru sahibi hesaplarını oluşturur.

    Returns:
        list[User]: Oluşturulan kullanıcılar.
    """
    return [
        user_service.create_user(
            f'aile{index + 1}@{DEMO_EMAIL_DOMAIN}', DEMO_PASSWORD,
            first_name=FIRST_NAMES[index % len(FIRST_NAMES)], last_name=LAST_NAMES[index % len(LAST_NAMES)],
        )
        for index in range(APPLICANT_COUNT)
    ]


def _create_inquiries(days, today, services, weights, rng):
    """
    Her gün için hafta içi daha yoğun olacak şekilde hızlı talepler üretir.

    Args:
        days (int): Geriye doğru gün sayısı.
        today (date): Bugün.
        services (list[ServiceType]): Aktif hizmetler.
        weights (list[int]): Hizmetlerin seçilme ağırlıkları.
        rng (random.Random): Rastgele sayı üreteci.

    Returns:
        int: Oluşturulan hızlı talep sayısı.
    """
    rows = []
    for offset in range(days):
        day = today - timedelta(days=offset)
        # Son haftalara doğru hafif artan, hafta sonu azalan talep.
        base = 3 if day.weekday() < 5 else 1
        for _index in range(rng.randint(0, base + (days - offset) // 30)):
            rows.append((
                ServiceInquiry(
                    full_name=f'{rng.choice(FIRST_NAMES)} {rng.choice(LAST_NAMES)}',
                    email=f'talep{len(rows) + 1}@{DEMO_EMAIL_DOMAIN}',
                    service=rng.choices(services, weights=weights)[0],
                    message=rng.choice(MESSAGES),
                    consent_given_at=timezone.now(),
                ),
                _moment(day, rng),
            ))
    created = ServiceInquiry.objects.bulk_create([row for row, _moment_value in rows])
    for inquiry, (_row, moment) in zip(created, rows):
        inquiry.created_at = moment
    ServiceInquiry.objects.bulk_update(created, ['created_at'])
    return len(created)


def _create_requests(days, today, services, weights, applicants, rng):
    """
    Başvuru sahiplerine dağıtılmış, yaşına göre durumu değişen başvurular üretir.

    Her başvurunun yaşlısı farklıdır; böylece aynı kişi ve hizmet için açık başvuru kuralı bozulmaz.

    Args:
        days (int): Geriye doğru gün sayısı.
        today (date): Bugün.
        services (list[ServiceType]): Aktif hizmetler.
        weights (list[int]): Hizmetlerin seçilme ağırlıkları.
        applicants (list[User]): Demo başvuru sahipleri.
        rng (random.Random): Rastgele sayı üreteci.

    Returns:
        int: Oluşturulan başvuru sayısı.
    """
    count = 0
    for offset in range(days):
        day = today - timedelta(days=offset)
        for _index in range(rng.choices([0, 1, 2], weights=[3, 4, 2])[0]):
            count += 1
            city, district = rng.choice(DISTRICTS)
            care_request = CareRequest.objects.create(
                applicant=rng.choice(applicants),
                service=rng.choices(services, weights=weights)[0],
                elder_full_name=f'{rng.choice(ELDER_FIRST_NAMES)} Demo{count}',
                elder_age=rng.randint(62, 94),
                relationship=rng.choice(CareRequest.Relationship.values),
                preferred_date=day + timedelta(days=rng.randint(2, 14)),
                time_slot=rng.choice(CareRequest.TimeSlot.values),
                city=city,
                district=district,
                address=f'Kurgu Sokak No: {count}',
                contact_phone='05550000000',
                consent_given_at=timezone.now(),
                status=_status_for_age(offset, rng),
            )
            CareRequest.objects.filter(pk=care_request.pk).update(created_at=_moment(day, rng))
    return count


def create_demo_data(days=90, seed=2026, today=None):
    """
    Son `days` güne yayılmış kurgusal başvuru sahipleri, hızlı talepler ve başvurular üretir.

    Aynı tohumla her çalıştırma aynı veriyi üretir. Demo verisi zaten varsa hiçbir şey yapılmaz;
    yeniden üretmek için önce `remove_demo_data` çağrılmalıdır.

    Args:
        days (int): Geriye doğru gün sayısı.
        seed (int): Rastgele sayı tohumu.
        today (Optional[date]): Bugünün tarihi; testler için verilebilir.

    Returns:
        dict[str, int]: `created` (oluşturulan satır sayısı) ve `updated` (her zaman 0).
    """
    if demo_data_exists():
        return {'created': 0, 'updated': 0}
    today = today or timezone.localdate()
    rng = random.Random(seed)
    services = list(ServiceType.objects.active())
    if not services:
        return {'created': 0, 'updated': 0}
    # İlk hizmetler daha çok talep görür; grafikte çizgiler birbirinden ayrışır.
    weights = [len(services) - index + 1 for index in range(len(services))]
    with transaction.atomic():
        applicants = _create_applicants()
        inquiries = _create_inquiries(days, today, services, weights, rng)
        requests = _create_requests(days, today, services, weights, applicants, rng)
    return {'created': len(applicants) + inquiries + requests, 'updated': 0}
