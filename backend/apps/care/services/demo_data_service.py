"""Geliştirme ortamında gösterge panelini anlamlı görmek için kurgusal demo verisi üretir."""

import random
from datetime import datetime, time, timedelta

import factory.random
from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import IntegrityError, transaction
from django.utils import timezone

from apps.accounts.factories import UserFactory
from apps.care.factories import CareRequestFactory, ServiceInquiryFactory
from apps.care.models import CareRequest, ServiceInquiry, ServiceType
from apps.geo.models import Neighborhood

# Demo kayıtları bu ayrılmış (gerçek olmayan) alan adındaki e-postalarla işaretlenir.
DEMO_EMAIL_DOMAIN = 'demo.yanimda.example'
APPLICANT_COUNT = 12
# Faker'ın ürettiği yaşlı adı nadiren aynı kişinin açık başvurusuyla çakışırsa yeni ad denenir.
MAX_NAME_ATTEMPTS = 5


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
    Verilen gün içinde gündüz saatlerine düşen rastgele bir zaman üretir.

    Args:
        day (date): Gün.
        rng (random.Random): Tekrarlanabilir rastgele sayı üreteci.

    Returns:
        datetime: Etkin saat dilimindeki zaman.
    """
    return timezone.make_aware(datetime.combine(day, time(hour=rng.randint(8, 21), minute=rng.randint(0, 59))))


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


def _neighborhood_picker(rng):
    """
    Mahalle seçen bir fonksiyon hazırlar; ilçelere farklı ağırlık verilerek haritada yoğunluk farkı oluşur.

    Args:
        rng (random.Random): Rastgele sayı üreteci.

    Returns:
        Callable[[], Neighborhood]: Her çağrıda ağırlıklı ilçeden rastgele bir mahalle döndüren fonksiyon.
    """
    by_district = {}
    for neighborhood in Neighborhood.objects.order_by('district_id', 'id'):
        by_district.setdefault(neighborhood.district_id, []).append(neighborhood)
    districts = list(by_district)
    weights = [rng.choice([1, 1, 2, 3, 5, 8, 13]) for _district in districts]

    def pick():
        """Ağırlıklı bir ilçe ve içinden bir mahalle seçer."""
        district = rng.choices(districts, weights=weights)[0]
        return rng.choice(by_district[district])

    return pick


def _create_applicants():
    """
    Kurgusal başvuru sahibi hesaplarını üretir; ad ve soyadı fabrikadaki Faker verir,
    parola `DEMO_USER_PASSWORD` ayarından okunur.

    Returns:
        list[User]: Oluşturulan kullanıcılar.
    """
    return [
        UserFactory(
            email=f'aile{number}@{DEMO_EMAIL_DOMAIN}',
            # Ham parola verilir; fabrikadaki Password dönüştürücüsü özetler.
            password=settings.DEMO_USER_PASSWORD,
        )
        for number in range(1, APPLICANT_COUNT + 1)
    ]


def _create_inquiries(days, today, services, weights, rng, pick_neighborhood):
    """
    Her gün için hafta içi daha yoğun olacak şekilde hızlı talepler üretir.

    Args:
        days (int): Geriye doğru gün sayısı.
        today (date): Bugün.
        services (list[ServiceType]): Aktif hizmetler.
        weights (list[int]): Hizmetlerin seçilme ağırlıkları.
        rng (random.Random): Rastgele sayı üreteci.
        pick_neighborhood (Callable[[], Neighborhood]): Mahalle seçici.

    Returns:
        int: Oluşturulan hızlı talep sayısı.
    """
    count = 0
    for offset in range(days):
        day = today - timedelta(days=offset)
        # Son haftalara doğru hafif artan, hafta sonu azalan talep.
        base = 3 if day.weekday() < 5 else 1
        for _index in range(rng.randint(0, base + (days - offset) // 30)):
            count += 1
            ServiceInquiryFactory(
                email=f'talep{count}@{DEMO_EMAIL_DOMAIN}',
                service=rng.choices(services, weights=weights)[0],
                neighborhood=pick_neighborhood(),
                created_at=_moment(day, rng),
            )
    return count


def _create_request(**fields):
    """
    Başvuruyu fabrikayla üretir; Faker'ın verdiği yaşlı adı aynı başvuru sahibinin
    aynı hizmetteki açık başvurusuyla çakışırsa yeni adla yeniden dener.

    Args:
        **fields (Any): CareRequestFactory alanları.

    Returns:
        CareRequest: Oluşturulan başvuru.

    Raises:
        IntegrityError: Tüm denemelerde çakışma sürerse.
    """
    for attempt in range(MAX_NAME_ATTEMPTS):
        try:
            with transaction.atomic():
                return CareRequestFactory(**fields)
        except IntegrityError:
            if attempt == MAX_NAME_ATTEMPTS - 1:
                raise
    return None


def _create_requests(days, today, services, weights, applicants, rng, pick_neighborhood):
    """
    Başvuru sahiplerine dağıtılmış, yaşına göre durumu değişen başvurular üretir.

    Yaşlı adı, yaş, yakınlık, zaman dilimi ve şehir fabrikadaki Faker tanımlarından gelir.

    Args:
        days (int): Geriye doğru gün sayısı.
        today (date): Bugün.
        services (list[ServiceType]): Aktif hizmetler.
        weights (list[int]): Hizmetlerin seçilme ağırlıkları.
        applicants (list[User]): Demo başvuru sahipleri.
        rng (random.Random): Rastgele sayı üreteci.
        pick_neighborhood (Callable[[], Neighborhood]): Mahalle seçici.

    Returns:
        int: Oluşturulan başvuru sayısı.
    """
    count = 0
    for offset in range(days):
        day = today - timedelta(days=offset)
        for _index in range(rng.choices([0, 1, 2], weights=[3, 4, 2])[0]):
            count += 1
            _create_request(
                applicant=rng.choice(applicants),
                service=rng.choices(services, weights=weights)[0],
                preferred_date=day + timedelta(days=rng.randint(2, 14)),
                neighborhood=pick_neighborhood(),
                status=_status_for_age(offset, rng),
                created_at=_moment(day, rng),
            )
    return count


def create_demo_data(days=90, seed=2026, today=None):
    """
    Son `days` güne yayılmış kurgusal başvuru sahipleri, hızlı talepler ve başvurular üretir.

    Kayıtları factory-boy fabrikaları, adları ve diğer kurgusal alanları fabrikaların Faker
    tanımları üretir. Aynı tohum hem bu modülün hem factory-boy/Faker'ın üretecine verildiği için her
    çalıştırma aynı veriyi verir. Demo verisi zaten varsa hiçbir şey yapılmaz; yeniden
    üretmek için önce `remove_demo_data` çağrılmalıdır.

    Args:
        days (int): Geriye doğru gün sayısı.
        seed (int): Rastgele sayı tohumu.
        today (Optional[date]): Bugünün tarihi; testler için verilebilir.

    Returns:
        dict[str, int]: `created` (oluşturulan satır sayısı) ve `updated` (her zaman 0).
    """
    if demo_data_exists():
        return {'created': 0, 'updated': 0}
    services = list(ServiceType.objects.active())
    # Hizmetler ve konumlar varsayılan veri komutlarıyla yüklenmemişse üretilecek bir şey yoktur.
    if not services or not Neighborhood.objects.exists():
        return {'created': 0, 'updated': 0}
    today = today or timezone.localdate()
    rng = random.Random(seed)
    factory.random.reseed_random(seed)
    # İlk hizmetler daha çok talep görür; grafikte çizgiler birbirinden ayrışır.
    weights = [len(services) - index + 1 for index in range(len(services))]
    with transaction.atomic():
        pick_neighborhood = _neighborhood_picker(rng)
        applicants = _create_applicants()
        inquiries = _create_inquiries(days, today, services, weights, rng, pick_neighborhood)
        requests = _create_requests(days, today, services, weights, applicants, rng, pick_neighborhood)
    return {'created': len(applicants) + inquiries + requests, 'updated': 0}
