from datetime import timedelta

from django.test import TestCase
from django.utils import timezone

from apps.care.factories import CareRequestFactory, ServiceInquiryFactory
from apps.care.services.map_service import build_map
from apps.care.tests.map_data import build_dataset, days_ago


class BuildMapTests(TestCase):
    """build_map servisinin ilçe ve mahalle sayımlarını doğrular."""

    def setUp(self):
        """Küçük harita veri kümesini kurar."""
        self.data = build_dataset()

    def district(self, result, district):
        """
        Sonuçtaki ilçe satırını döndürür.

        Args:
            result (dict): build_map sonucu.
            district (District): Aranan ilçe.

        Returns:
            dict: İlçe satırı.
        """
        return next(item for item in result['districts'] if item['id'] == district.id)

    def test_total_and_services(self):
        """
        Toplamın ve hizmet sayımlarının doğru hesaplandığını doğrular.

        Senaryo:
        - Mahallesi olan 5 ve olmayan 1 kayıt bulunur.

        Beklenti:
        - Toplam 5, hizmet sayıları 3 ve 2 olmalıdır.
        """
        result = build_map()

        self.assertEqual(result['total'], 5)
        counts = {item['id']: item['count'] for item in result['services']}
        self.assertEqual(counts[self.data.s1.id], 3)
        self.assertEqual(counts[self.data.s2.id], 2)

    def test_districts_by_service(self):
        """
        İlçe toplamlarının ve hizmet kırılımının doğru olduğunu doğrular.

        Senaryo:
        - Birinci ilçede iki mahalle, ikincide bir mahalle kaydı vardır.

        Beklenti:
        - Sayılar ve by_service sözlükleri beklenen değerlerde olmalıdır.
        """
        result = build_map()

        first = self.district(result, self.data.d1)
        self.assertEqual(first['count'], 4)
        self.assertEqual(first['by_service'], {str(self.data.s1.id): 3, str(self.data.s2.id): 1})
        second = self.district(result, self.data.d2)
        self.assertEqual((second['count'], second['by_service']), (1, {str(self.data.s2.id): 1}))

    def test_zero_districts_included_in_order(self):
        """
        Kaydı olmayan ilçenin de sıfırla döndüğünü ve sıranın korunduğunu doğrular.

        Senaryo:
        - Üçüncü ilçenin mahallesinde kayıt yoktur.

        Beklenti:
        - İlçe sayısı 0, by_service boş; ilçeler sort_order sırasındadır.
        """
        result = build_map()

        empty = self.district(result, self.data.d3)
        self.assertEqual((empty['count'], empty['by_service']), (0, {}))
        ids = [item['id'] for item in result['districts']]
        self.assertLess(ids.index(self.data.d1.id), ids.index(self.data.d2.id))
        self.assertLess(ids.index(self.data.d2.id), ids.index(self.data.d3.id))

    def test_neighborhoods_sorted_and_zero_excluded(self):
        """
        Mahallelerin sayıya göre azalan sıralandığını ve sıfırların dışlandığını doğrular.

        Senaryo:
        - Üç mahallede sırasıyla 3, 1, 1 kayıt; dördüncüde 0 kayıt vardır.

        Beklenti:
        - Yalnızca üç mahalle döner, ilki 3 kayıtlıdır; district_id ve by_service dolu olmalıdır.
        """
        result = build_map()

        neighborhoods = result['neighborhoods']
        self.assertEqual(len(neighborhoods), 3)
        self.assertEqual(neighborhoods[0]['id'], self.data.n1.id)
        self.assertEqual(neighborhoods[0]['count'], 3)
        self.assertEqual(neighborhoods[0]['district_id'], self.data.d1.id)
        self.assertEqual(neighborhoods[0]['by_service'], {str(self.data.s1.id): 3})
        self.assertNotIn(self.data.n4.id, [item['id'] for item in neighborhoods])
        counts = [item['count'] for item in neighborhoods]
        self.assertEqual(counts, sorted(counts, reverse=True))

    def test_source_filtering(self):
        """
        Kaynak seçiminin yalnızca ilgili kayıtları saydığını doğrular.

        Senaryo:
        - Mahalleli 3 hızlı talep ve 2 başvuru vardır.

        Beklenti:
        - inquiries 3, requests 2, all 5 toplam vermelidir.
        """
        self.assertEqual(build_map(source='inquiries')['total'], 3)
        self.assertEqual(build_map(source='requests')['total'], 2)
        self.assertEqual(build_map(source='all')['total'], 5)

    def test_days_filtering(self):
        """
        Gün aralığının sınır günü dahil olacak şekilde uygulandığını doğrular.

        Senaryo:
        - Mevcut kayıtlara 10 ve 40 gün önceki iki kayıt eklenir; 30 günlük sayım yapılır.
        - Ardından 29 ve 30 gün önceki iki başvuru eklenip tekrar sayılır.

        Beklenti:
        - 40 gün öncesi dışlanır; 29 gün öncesi dahil, 30 gün öncesi dışlanır.
        """
        ServiceInquiryFactory(service=self.data.s1, neighborhood=self.data.n3, created_at=days_ago(10))
        ServiceInquiryFactory(service=self.data.s1, neighborhood=self.data.n3, created_at=days_ago(40))

        self.assertEqual(build_map(days=30)['total'], 6)
        self.assertEqual(build_map()['total'], 7)

        CareRequestFactory(service=self.data.s1, neighborhood=self.data.n3, created_at=days_ago(29))
        CareRequestFactory(service=self.data.s1, neighborhood=self.data.n3, created_at=days_ago(30))
        self.assertEqual(build_map(days=30)['total'], 7)

    def test_days_with_today_argument(self):
        """
        today parametresinin pencerenin başlangıcını belirlediğini doğrular.

        Senaryo:
        - Bugünkü kayıtlar varken today 100 gün sonrası verilir.

        Beklenti:
        - Hiçbir kayıt pencereye girmez; toplam 0 olur.
        """
        far_future = timezone.localdate() + timedelta(days=100)

        self.assertEqual(build_map(days=30, today=far_future)['total'], 0)

    def test_records_without_neighborhood_ignored(self):
        """
        Mahallesiz kayıtların hiçbir sayıma girmediğini doğrular.

        Senaryo:
        - Mevcut sayımlar alınır, ardından mahallesiz bir hızlı talep eklenir.

        Beklenti:
        - Toplam ve hizmet sayıları değişmemelidir.
        """
        before = build_map()
        ServiceInquiryFactory(service=self.data.s2, neighborhood=None)

        after = build_map()

        self.assertEqual(before['total'], after['total'])
        self.assertEqual(before['services'], after['services'])
