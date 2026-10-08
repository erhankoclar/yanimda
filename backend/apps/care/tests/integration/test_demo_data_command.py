from datetime import date, timedelta
from io import StringIO

from django.contrib.auth import authenticate, get_user_model
from django.core.management import call_command
from django.core.management.base import CommandError
from django.db.models import Count, Max, Min
from django.test import TestCase, override_settings
from django.utils import timezone
from django.utils.translation import gettext

from apps.care.models import CareRequest, ServiceInquiry
from apps.care.services import demo_data_service, service_type_service
from apps.care.tests.factories import make_service
from apps.geo.factories import NeighborhoodFactory

STAR_LINE = '*' * 78
DASH_LINE = '-' * 78
DEMO_SUFFIX = f'@{demo_data_service.DEMO_EMAIL_DOMAIN}'


def run_command(*args):
    """
    care_create_demo_data komutunu çalıştırır ve çıktısını satırlarına ayırır.

    Args:
        *args (str): Komut seçenekleri (ör. `--reset`).

    Returns:
        list[str]: Komutun standart çıktı satırları.
    """
    out = StringIO()
    call_command('care_create_demo_data', *args, stdout=out, stderr=StringIO())
    return out.getvalue().splitlines()


@override_settings(DEBUG=True)
class CareCreateDemoDataTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        """Demo verisinin dağıtılacağı varsayılan hizmetleri kurar."""
        service_type_service.create_default_service_types()
        for _index in range(6):
            NeighborhoodFactory()

    def test_creates_fictional_applicants_inquiries_and_requests(self):
        """
        Komutun yalnızca demo alan adlı kurgusal kayıtlar ürettiğini doğrular.

        Senaryo:
        - Boş veritabanında komut çalıştırılır.

        Beklenti:
        - Demo başvuru sahipleri, hızlı talepler ve başvurular oluşmalı.
        - Tüm e-postalar ayrılmış demo alan adında olmalı; kullanıcılar admin olmamalıdır.
        """
        run_command()

        users = get_user_model().objects.all()
        self.assertEqual(users.count(), demo_data_service.APPLICANT_COUNT)
        self.assertFalse(users.exclude(email__endswith=DEMO_SUFFIX).exists())
        self.assertFalse(users.filter(is_staff=True).exists())
        self.assertGreater(ServiceInquiry.objects.count(), 0)
        self.assertFalse(ServiceInquiry.objects.exclude(email__endswith=DEMO_SUFFIX).exists())
        self.assertGreater(CareRequest.objects.count(), 0)

    def test_every_record_gets_a_neighborhood(self):
        """
        Komutun ürettiği her başvuru ve hızlı talebe veritabanındaki bir mahalle atadığını doğrular.

        Senaryo:
        - Mahalleler setUpTestData'da yüklüyken komut çalıştırılır.

        Beklenti:
        - Mahallesiz kayıt kalmamalı; kayıtlar birden fazla mahalleye dağılmalıdır.
        """
        run_command('--days', '30')

        self.assertTrue(CareRequest.objects.exists())
        self.assertTrue(ServiceInquiry.objects.exists())
        self.assertFalse(CareRequest.objects.filter(neighborhood__isnull=True).exists())
        self.assertFalse(ServiceInquiry.objects.filter(neighborhood__isnull=True).exists())
        self.assertGreater(CareRequest.objects.values('neighborhood').distinct().count(), 1)

    def test_spreads_records_over_the_requested_days(self):
        """
        Kayıt tarihlerinin istenen gün aralığına yayıldığını doğrular.

        Senaryo:
        - Komut `--days 30` ile çalıştırılır.

        Beklenti:
        - En eski kayıt 30 günden eski olmamalı, en yeni kayıt bugünden ileri olmamalıdır.
        - Kayıtlar tek güne yığılmamalı, birden fazla güne dağılmalıdır.
        """
        run_command('--days', '30')

        today = timezone.localdate()
        for model in (ServiceInquiry, CareRequest):
            bounds = model.objects.aggregate(first=Min('created_at'), last=Max('created_at'))
            self.assertGreaterEqual(timezone.localtime(bounds['first']).date(), today - timedelta(days=29))
            self.assertLessEqual(timezone.localtime(bounds['last']).date(), today)
        days = {timezone.localtime(value).date() for value in ServiceInquiry.objects.values_list('created_at', flat=True)}
        self.assertGreater(len(days), 10)

    def test_old_requests_are_closed_and_recent_ones_open(self):
        """
        Başvuru durumlarının yaşa göre gerçekçi dağıldığını doğrular.

        Senaryo:
        - Komut varsayılan 90 günle çalıştırılır.

        Beklenti:
        - 20 günden eski başvuruların hepsi tamamlanmış veya iptal edilmiş olmalıdır.
        - Son bir haftanın başvuruları açık (yeni veya inceleniyor) olmalıdır.
        """
        run_command()

        today = timezone.localdate()
        old = CareRequest.objects.filter(created_at__date__lt=today - timedelta(days=21))
        recent = CareRequest.objects.filter(created_at__date__gte=today - timedelta(days=6))
        self.assertTrue(old.exists())
        self.assertFalse(old.exclude(status__in=[CareRequest.Status.COMPLETED, CareRequest.Status.CANCELLED]).exists())
        self.assertFalse(recent.exclude(status__in=[CareRequest.Status.NEW, CareRequest.Status.REVIEWING]).exists())

    def test_second_run_is_idempotent(self):
        """
        Komutun ikinci çalıştırmada yeni kayıt oluşturmadığını doğrular.

        Senaryo:
        - Komut iki kez çalıştırılır.

        Beklenti:
        - Kayıt sayıları değişmemeli, ikinci özet 0/0 göstermelidir.
        """
        run_command()
        counts = (ServiceInquiry.objects.count(), CareRequest.objects.count())

        lines = run_command()

        self.assertEqual((ServiceInquiry.objects.count(), CareRequest.objects.count()), counts)
        expected = gettext(
            'All care demo data operations completed. Created: %(created)d, Updated: %(updated)d.'
        ) % {'created': 0, 'updated': 0}
        self.assertIn(expected, lines)

    def test_reset_recreates_demo_data_without_touching_real_records(self):
        """
        `--reset` seçeneğinin yalnızca demo verisini silip yeniden ürettiğini doğrular.

        Senaryo:
        - Demo dışı bir kullanıcı ve hızlı talep vardır; komut önce normal, sonra `--reset` ile çalışır.

        Beklenti:
        - Demo dışı kayıtlar korunmalı, aynı tohumla aynı sayıda demo kaydı yeniden oluşmalıdır.
        - Çıktıda iki adım ve silinen satır sayısı bulunmalıdır.
        """
        real_user = get_user_model().objects.create_user('gercek@example.com', 'Kurgusal-Parola-1')
        real_inquiry = ServiceInquiry.objects.create(
            full_name='Gerçek Kişi', email='gercek@example.com', service=make_service(),
            message='Kurgusal talep metni.', consent_given_at=timezone.now(),
        )
        run_command()
        demo_count = ServiceInquiry.objects.filter(email__endswith=DEMO_SUFFIX).count()

        lines = run_command('--reset')

        self.assertTrue(get_user_model().objects.filter(pk=real_user.pk).exists())
        self.assertTrue(ServiceInquiry.objects.filter(pk=real_inquiry.pk).exists())
        self.assertEqual(ServiceInquiry.objects.filter(email__endswith=DEMO_SUFFIX).count(), demo_count)
        self.assertTrue(any(line.startswith('[2/2]') for line in lines))
        self.assertTrue(any(line.startswith(gettext('Removed rows: %(count)d.').split('%')[0]) for line in lines))

    def test_output_uses_the_standard_separators(self):
        """
        Konsol çıktısının ortak komut biçimine uyduğunu doğrular.

        Senaryo:
        - Komut tek adımla (sıfırlamasız) çalıştırılır.

        Beklenti:
        - `*` ayıracı yalnızca ilk ve son satırda, `-` ayıracı adım öncesi ve özet öncesi olmak üzere iki kez bulunmalıdır.
        """
        lines = run_command()

        self.assertEqual(lines[0], STAR_LINE)
        self.assertEqual(lines[-1], STAR_LINE)
        self.assertEqual(lines.count(STAR_LINE), 2)
        self.assertEqual(lines.count(DASH_LINE), 2)

    def test_same_seed_produces_the_same_data(self):
        """
        Aynı tohum ve tarihle üretilen verinin aynı olduğunu doğrular.

        Senaryo:
        - Sabit bir günde veri üretilir, silinir ve aynı günle yeniden üretilir.

        Beklenti:
        - Hizmet başına hızlı talep sayıları iki üretimde aynı olmalıdır.
        """
        fixed_day = date(2026, 10, 8)
        demo_data_service.create_demo_data(today=fixed_day)
        first = list(ServiceInquiry.objects.values('service').annotate(count=Count('id')).order_by('service'))
        demo_data_service.remove_demo_data()

        demo_data_service.create_demo_data(today=fixed_day)

        second = list(ServiceInquiry.objects.values('service').annotate(count=Count('id')).order_by('service'))
        self.assertEqual(first, second)


    def test_demo_accounts_use_the_password_from_settings(self):
        """
        Demo hesaplarının parolasının `DEMO_USER_PASSWORD` ayarından geldiğini doğrular.

        Senaryo:
        - Ayar dışarıdan değiştirilerek komut çalıştırılır.

        Beklenti:
        - Demo hesabı yeni ayardaki parolayla doğrulanabilmelidir.
        """
        with override_settings(DEMO_USER_PASSWORD='Demo-Disaridan-3'):
            run_command('--days', '7')

        email = f'aile1{DEMO_SUFFIX}'
        self.assertIsNotNone(authenticate(email=email, password='Demo-Disaridan-3'))


class CareCreateDemoDataGuardTests(TestCase):
    @override_settings(DEBUG=False)
    def test_refuses_to_run_without_debug(self):
        """
        DEBUG kapalıyken komutun hiçbir kayıt yazmadan hata verdiğini doğrular (hata yolu).

        Senaryo:
        - DEBUG=False ayarıyla komut çalıştırılır.

        Beklenti:
        - CommandError fırlatılmalı ve hiçbir kullanıcı veya talep oluşmamalıdır.
        """
        service_type_service.create_default_service_types()

        with self.assertRaisesMessage(CommandError, gettext('Demo data can only be created when DEBUG is enabled.')):
            run_command()

        self.assertFalse(get_user_model().objects.exists())
        self.assertFalse(ServiceInquiry.objects.exists())


@override_settings(DEBUG=True)
class CareCreateDemoDataWithoutLocationsTests(TestCase):
    def test_creates_nothing_without_neighborhoods(self):
        """
        Veritabanında mahalle yokken komutun hiçbir kayıt üretmediğini doğrular (sınır durumu).

        Senaryo:
        - Hizmetler yüklüdür ama mahalle yoktur; komut çalıştırılır.

        Beklenti:
        - Kullanıcı, başvuru ve hızlı talep oluşmamalıdır.
        """
        service_type_service.create_default_service_types()

        run_command('--days', '7')

        self.assertFalse(get_user_model().objects.exists())
        self.assertFalse(CareRequest.objects.exists())
        self.assertFalse(ServiceInquiry.objects.exists())
