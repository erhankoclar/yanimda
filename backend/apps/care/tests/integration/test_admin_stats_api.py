from datetime import timedelta

from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from apps.care.models import CareRequest
from apps.care.stats import DAILY_SERIES_DAYS
from apps.care.tests.factories import make_care_request, make_service, make_user


class AdminStatsApiTests(APITestCase):
    def setUp(self):
        """Admin kullanıcıyla oturum açar."""
        self.client.force_authenticate(make_user(is_staff=True))
        self.url = reverse('care-admin:stats')

    def test_counts_requests_and_applicants(self):
        """
        Toplam, açık, son 7 gün ve başvuru sahibi sayılarının doğru hesaplandığını doğrular.

        Senaryo:
        - Biri tamamlanmış, biri iptal, biri 10 gün önce oluşturulmuş dört talep hazırlanır.
        - Ayrıca pasif bir standart kullanıcı oluşturulur.

        Beklenti:
        - Toplam 4, açık 2, son 7 gün 3 olmalı; başvuru sahibi sayısı yalnızca aktif standart kullanıcıları saymalıdır.
        """
        make_care_request()
        make_care_request(status=CareRequest.Status.COMPLETED)
        make_care_request(status=CareRequest.Status.CANCELLED)
        old = make_care_request()
        CareRequest.objects.filter(pk=old.pk).update(created_at=timezone.now() - timedelta(days=10))
        make_user(is_active=False)

        data = self.client.get(self.url).data

        self.assertEqual(data['total_requests'], 4)
        self.assertEqual(data['open_requests'], 2)
        self.assertEqual(data['requests_last_7_days'], 3)
        self.assertEqual(data['total_applicants'], 4)

    def test_breakdowns_include_zero_counts(self):
        """
        Durum ve hizmet dağılımlarının sıfır sayıları da içerdiğini doğrular.

        Senaryo:
        - Talebi olmayan bir hizmet ile tek talepli bir hizmet hazırlanır.

        Beklenti:
        - Tüm durumlar akış sırasıyla listelenmeli; talepsiz hizmet 0 ile görünmelidir.
        """
        empty_service = make_service(sort_order=1)
        used_service = make_service(sort_order=2)
        make_care_request(service=used_service)

        data = self.client.get(self.url).data

        self.assertEqual([item['status'] for item in data['by_status']], CareRequest.Status.values)
        self.assertEqual(data['by_status'][0]['count'], 1)
        counts = {item['service_id']: item['count'] for item in data['by_service']}
        self.assertEqual(counts, {empty_service.id: 0, used_service.id: 1})

    def test_daily_series_covers_last_14_days(self):
        """
        Günlük serinin bugün dahil son 14 günü eski tarihten yeniye kapsadığını doğrular (sınır değer).

        Senaryo:
        - Bugün iki, 13 gün önce bir ve 14 gün önce bir talep oluşturulur.

        Beklenti:
        - Seri 14 gün olmalı; ilk gün 1, son gün 2 olmalı, 14 gün önceki talep sayılmamalıdır.
        """
        today = timezone.localdate()
        make_care_request()
        make_care_request()
        for days in (13, 14):
            care_request = make_care_request()
            CareRequest.objects.filter(pk=care_request.pk).update(created_at=timezone.now() - timedelta(days=days))

        daily = self.client.get(self.url).data['daily']

        self.assertEqual(len(daily), DAILY_SERIES_DAYS)
        self.assertEqual(daily[0]['date'], (today - timedelta(days=13)).isoformat())
        self.assertEqual(daily[-1]['date'], today.isoformat())
        self.assertEqual(daily[0]['count'], 1)
        self.assertEqual(daily[-1]['count'], 2)

    def test_empty_database_returns_zeros(self):
        """Hiç veri yokken istatistiklerin sıfır değerlerle döndüğünü doğrular (uç durum)."""
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['total_requests'], 0)
        self.assertEqual(response.data['by_service'], [])
        self.assertTrue(all(item['count'] == 0 for item in response.data['daily']))
