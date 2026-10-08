from datetime import date

from django.test import SimpleTestCase

from apps.care.services.dashboard_service import bucket_starts, change_percent, month_periods


class ChangePercentTests(SimpleTestCase):
    def test_rounded_increase_and_decrease(self):
        """
        Yüzde değişimin artış ve azalışta doğru yuvarlandığını doğrular.

        Senaryo:
        - 10'dan 15'e, 12'den 9'a ve 3'ten 4'e değişim hesaplanır.

        Beklenti:
        - Sırasıyla 50, -25 ve 33 dönmelidir.
        """
        self.assertEqual(change_percent(15, 10), 50)
        self.assertEqual(change_percent(9, 12), -25)
        self.assertEqual(change_percent(4, 3), 33)

    def test_zero_previous_has_no_comparison(self):
        """Önceki dönem 0 olduğunda kıyasın None döndüğünü doğrular (sıfıra bölme uç durumu)."""
        self.assertIsNone(change_percent(5, 0))
        self.assertIsNone(change_percent(0, 0))


class MonthPeriodsTests(SimpleTestCase):
    def test_same_days_of_previous_month(self):
        """
        Bu ay ile geçen ayın aynı gün aralığının hesaplandığını doğrular.

        Senaryo:
        - Bugün 8 Ekim kabul edilir.

        Beklenti:
        - Bu ay 1-8 Ekim, geçen ay 1-8 Eylül olmalıdır.
        """
        this, previous = month_periods(date(2026, 10, 8))

        self.assertEqual(this, (date(2026, 10, 1), date(2026, 10, 8)))
        self.assertEqual(previous, (date(2026, 9, 1), date(2026, 9, 8)))

    def test_previous_month_shorter_is_capped(self):
        """Geçen ay daha kısaysa aralığın o ayın son gününde bittiğini doğrular (31 Mart → 28 Şubat)."""
        _this, previous = month_periods(date(2027, 3, 31))

        self.assertEqual(previous, (date(2027, 2, 1), date(2027, 2, 28)))

    def test_january_compares_with_december(self):
        """Ocak ayının bir önceki yılın Aralık ayıyla kıyaslandığını doğrular (yıl geçişi)."""
        _this, previous = month_periods(date(2027, 1, 15))

        self.assertEqual(previous, (date(2026, 12, 1), date(2026, 12, 15)))


class BucketStartsTests(SimpleTestCase):
    def test_daily_buckets_include_both_ends(self):
        """Günlük dönemlerin ilk ve son günü dahil ettiğini doğrular."""
        starts = bucket_starts(date(2026, 10, 2), date(2026, 10, 8), 'day')

        self.assertEqual(len(starts), 7)
        self.assertEqual((starts[0], starts[-1]), (date(2026, 10, 2), date(2026, 10, 8)))

    def test_weekly_buckets_start_on_monday(self):
        """
        Haftalık dönemlerin pazartesi başladığını doğrular.

        Senaryo:
        - Cumartesi başlayan bir aralık haftalık gruplanır.

        Beklenti:
        - İlk dönem önceki pazartesi olmalı ve tüm dönemler pazartesi başlamalıdır.
        """
        starts = bucket_starts(date(2026, 7, 11), date(2026, 10, 8), 'week')

        self.assertEqual(starts[0], date(2026, 7, 6))
        self.assertTrue(all(start.weekday() == 0 for start in starts))
        self.assertEqual(starts[-1], date(2026, 10, 5))
