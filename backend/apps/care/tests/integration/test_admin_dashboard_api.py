from datetime import timedelta

from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from apps.care.services.dashboard_service import month_periods
from apps.care.models import CareRequest, ServiceInquiry
from apps.care.tests.factories import make_care_request, make_service, make_user


def make_inquiry(service, days_ago=0, **overrides):
    """
    Belirtilen gün kadar geriye tarihlenmiş hızlı talep oluşturur.

    Args:
        service (ServiceType): Talep edilen hizmet.
        days_ago (int): Kaç gün önce oluşturulmuş sayılacağı.
        **overrides (Any): Model alanlarını ezen değerler.

    Returns:
        ServiceInquiry: Oluşturulan talep.
    """
    data = {
        'full_name': 'Deneme Kişi', 'email': 'd@example.com', 'service': service,
        'message': 'Kurgusal açıklama', 'consent_given_at': timezone.now(), **overrides,
    }
    inquiry = ServiceInquiry.objects.create(**data)
    if days_ago:
        ServiceInquiry.objects.filter(pk=inquiry.pk).update(created_at=timezone.now() - timedelta(days=days_ago))
    return inquiry


def backdate(care_request, days_ago):
    """
    Başvurunun oluşturulma zamanını geriye alır.

    Args:
        care_request (CareRequest): Başvuru.
        days_ago (int): Kaç gün önce oluşturulmuş sayılacağı.
    """
    CareRequest.objects.filter(pk=care_request.pk).update(created_at=timezone.now() - timedelta(days=days_ago))


class AdminDashboardApiTests(APITestCase):
    def setUp(self):
        """Admin oturumu ve iki aktif, bir pasif hizmet hazırlar."""
        self.client.force_authenticate(make_user(is_staff=True))
        self.url = reverse('care-admin:dashboard')
        self.companion = make_service(name='Refakat', sort_order=1)
        self.hospital = make_service(name='Hastane', sort_order=2)
        make_service(name='Pasif', sort_order=3, is_active=False)

    def get(self, **params):
        """
        Dashboard'u parametrelerle çağırır.

        Args:
            **params (Any): Sorgu parametreleri.

        Returns:
            dict[str, Any]: Yanıt verisi.
        """
        response = self.client.get(self.url, params)
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        return response.data

    def test_cards_compare_this_month_with_same_days_of_previous_month(self):
        """
        Kartların bu ayı geçen ayın aynı günleriyle kıyasladığını doğrular.

        Senaryo:
        - Bu ay 2 hızlı talep ve 1 başvuru, geçen ayın aynı aralığında 2 hızlı talep oluşturulur.

        Beklenti:
        - Toplam talep 3, önceki 2, değişim %50 olmalı; hızlı talepte değişim %0 olmalıdır.
        """
        today = timezone.localdate()
        (_this_start, _), (previous_start, _) = month_periods(today)
        days_to_previous = (today - previous_start).days
        make_inquiry(self.companion)
        make_inquiry(self.hospital)
        make_care_request(service=self.companion)
        make_inquiry(self.companion, days_ago=days_to_previous)
        make_inquiry(self.hospital, days_ago=days_to_previous)

        cards = self.get()['cards']

        self.assertEqual(cards['total_demand'], {'value': 3, 'previous': 2, 'change_percent': 50})
        self.assertEqual(cards['inquiries'], {'value': 2, 'previous': 2, 'change_percent': 0})

    def test_open_requests_and_services_cards(self):
        """
        Bekleyen başvuru ve hizmet kartlarını doğrular.

        Senaryo:
        - Biri yeni, biri inceleniyor, biri tamamlanmış üç başvuru; refakate ek iki hızlı talep oluşturulur.

        Beklenti:
        - Açık başvuru 2, incelenmemiş 1 olmalı; aktif hizmet 2 ve en çok talep alan refakat olmalıdır.
        """
        make_care_request(service=self.hospital)
        make_care_request(service=self.hospital, status=CareRequest.Status.REVIEWING)
        make_care_request(service=self.hospital, status=CareRequest.Status.COMPLETED)
        for _index in range(4):
            make_inquiry(self.companion)

        cards = self.get()['cards']

        self.assertEqual(cards['open_requests'], {'value': 2, 'new': 1})
        self.assertEqual(cards['services'], {'value': 2, 'top_service': 'Refakat'})

    def test_series_has_one_zero_filled_line_per_active_service(self):
        """
        Grafik serisinin her aktif hizmet için sıfırla doldurulmuş bir çizgi verdiğini doğrular.

        Senaryo:
        - Bugün refakate bir talep ve bir başvuru, 2 gün önce hastaneye bir talep oluşturulur.
        - 7 günlük seri istenir.

        Beklenti:
        - 7 günlük etiket ve 2 çizgi olmalı; refakatin son günü 2, hastanenin 2 gün önceki değeri 1 olmalıdır.
        """
        make_inquiry(self.companion)
        make_care_request(service=self.companion)
        make_inquiry(self.hospital, days_ago=2)

        series = self.get(days=7)['series']

        self.assertEqual(series['bucket'], 'day')
        self.assertEqual(len(series['labels']), 7)
        self.assertEqual(series['labels'][-1], timezone.localdate().isoformat())
        lines = {line['name']: line['counts'] for line in series['datasets']}
        self.assertEqual(set(lines), {'Refakat', 'Hastane'})
        self.assertEqual(lines['Refakat'], [0, 0, 0, 0, 0, 0, 2])
        self.assertEqual(lines['Hastane'], [0, 0, 0, 0, 1, 0, 0])

    def test_source_filter_counts_only_selected_records(self):
        """
        Grafikteki kaynak seçiminin yalnızca seçilen kayıt türünü saydığını doğrular.

        Senaryo:
        - Refakate bugün bir hızlı talep ve bir başvuru oluşturulur; üç kaynak ayrı ayrı istenir.

        Beklenti:
        - Bugünkü değer tümünde 2, hızlı taleplerde 1, başvurularda 1 olmalıdır.
        """
        make_inquiry(self.companion)
        make_care_request(service=self.companion)

        def today_count(source):
            datasets = self.get(days=7, source=source)['series']['datasets']
            return next(line for line in datasets if line['name'] == 'Refakat')['counts'][-1]

        self.assertEqual((today_count('all'), today_count('inquiries'), today_count('requests')), (2, 1, 1))

    def test_ninety_days_are_grouped_by_week(self):
        """
        90 günlük aralığın haftalık gruplandığını ve eski kayıtların aralık dışında kaldığını doğrular.

        Senaryo:
        - 100 gün önce ve bugün birer hızlı talep oluşturulur; 90 günlük seri istenir.

        Beklenti:
        - Dönem `week` olmalı, toplamda yalnızca bugünkü talep sayılmalıdır.
        """
        make_inquiry(self.companion)
        make_inquiry(self.companion, days_ago=100)

        series = self.get(days=90)['series']

        self.assertEqual(series['bucket'], 'week')
        self.assertLessEqual(len(series['labels']), 14)
        refakat = next(line for line in series['datasets'] if line['name'] == 'Refakat')
        self.assertEqual(sum(refakat['counts']), 1)

    def test_recent_merges_inquiries_and_requests_newest_first(self):
        """
        Son kayıtların hızlı talepler ve başvurular birleşik, en yeniden eskiye geldiğini doğrular.

        Senaryo:
        - 3 gün önce bir başvuru, 2 gün önce bir hızlı talep ve bugün bir başvuru oluşturulur.

        Beklenti:
        - Sıra: bugünkü başvuru, hızlı talep, eski başvuru; başlık ve tür doğru olmalıdır.
        """
        old_request = make_care_request(service=self.hospital, elder_full_name='Eski Yaşlı')
        backdate(old_request, 3)
        make_inquiry(self.companion, days_ago=2, full_name='Talep Sahibi')
        make_care_request(service=self.companion, elder_full_name='Yeni Yaşlı')

        recent = self.get()['recent']

        self.assertEqual(
            [(item['type'], item['title']) for item in recent],
            [('request', 'Yeni Yaşlı'), ('inquiry', 'Talep Sahibi'), ('request', 'Eski Yaşlı')],
        )
        self.assertIsNone(recent[1]['status'])

    def test_pending_lists_oldest_new_or_reviewing_requests(self):
        """
        Bekleyen işlerin en eski yeni/inceleniyor başvurulardan oluştuğunu doğrular.

        Senaryo:
        - Farklı yaşta yeni ve inceleniyor başvurular ile bir atandı başvurusu oluşturulur.

        Beklenti:
        - Atandı başvurusu listede olmamalı; en eski önce gelmelidir.
        """
        newest = make_care_request(service=self.companion)
        oldest = make_care_request(service=self.companion, status=CareRequest.Status.REVIEWING)
        backdate(oldest, 5)
        assigned = make_care_request(service=self.companion, status=CareRequest.Status.ASSIGNED)
        backdate(assigned, 9)

        pending = self.get()['pending']

        self.assertEqual([item['id'] for item in pending], [oldest.id, newest.id])

    def test_invalid_parameters_are_rejected(self):
        """Geçersiz gün sayısı ve kaynak için 400 döndüğünü doğrular (hata yolu)."""
        for params in ({'days': 15}, {'source': 'hepsi'}):
            with self.subTest(params=params):
                response = self.client.get(self.url, params)
                self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
