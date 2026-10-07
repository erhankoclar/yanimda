from datetime import timedelta

from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from apps.care.models import CareRequest
from apps.care.tests.factories import make_care_request, make_service, make_user


class AdminRequestListApiTests(APITestCase):
    def setUp(self):
        """Admin kullanıcıyla oturum açar."""
        self.admin = make_user(is_staff=True)
        self.client.force_authenticate(self.admin)
        self.url = reverse('care-admin:request-list')

    def ids(self, **params):
        """
        Admin talep listesini parametrelerle çağırıp dönen talep kimliklerini verir.

        Args:
            **params (Any): Sorgu parametreleri.

        Returns:
            list[int]: Sonuç sırasına göre talep kimlikleri.
        """
        response = self.client.get(self.url, params)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        return [item['id'] for item in response.data['results']]

    def test_lists_requests_of_all_applicants_newest_first(self):
        """
        Admin listesinin tüm başvuru sahiplerinin taleplerini en yeniden eskiye döndürdüğünü doğrular.

        Senaryo:
        - İki farklı kullanıcı için talep oluşturulur, ilki geriye tarihlenir.

        Beklenti:
        - Her iki talep de yeni olan önce gelecek şekilde listelenmelidir.
        """
        older = make_care_request()
        newer = make_care_request()
        CareRequest.objects.filter(pk=older.pk).update(created_at=timezone.now() - timedelta(days=1))

        self.assertEqual(self.ids(), [newer.id, older.id])

    def test_filters_by_status_service_and_applicant(self):
        """
        Durum, hizmet ve başvuru sahibi filtrelerinin listeyi daralttığını doğrular.

        Senaryo:
        - Farklı durum, hizmet ve kullanıcıya sahip talepler oluşturulur.
        - Her filtre ayrı ayrı uygulanır.

        Beklenti:
        - Her filtre yalnızca eşleşen talebi döndürmelidir.
        """
        service = make_service()
        applicant = make_user()
        by_status = make_care_request(status=CareRequest.Status.ASSIGNED)
        by_service = make_care_request(service=service)
        by_applicant = make_care_request(applicant=applicant)

        self.assertEqual(self.ids(status='assigned'), [by_status.id])
        self.assertEqual(self.ids(service=service.id), [by_service.id])
        self.assertEqual(self.ids(applicant=applicant.id), [by_applicant.id])

    def test_filters_by_creation_date_range(self):
        """
        Oluşturulma tarihi aralığı filtresinin uç günleri dahil ettiğini doğrular (sınır değer).

        Senaryo:
        - 10, 5 ve 0 gün önce oluşturulmuş talepler hazırlanır.
        - 5 gün öncesinden bugüne aralık filtrelenir.

        Beklenti:
        - 5 gün önceki ve bugünkü talepler dönmeli, 10 gün önceki dönmemelidir.
        """
        today = timezone.localdate()
        old, edge, fresh = make_care_request(), make_care_request(), make_care_request()
        for care_request, days in ((old, 10), (edge, 5)):
            CareRequest.objects.filter(pk=care_request.pk).update(created_at=timezone.now() - timedelta(days=days))

        result = self.ids(created_from=(today - timedelta(days=5)).isoformat(), created_to=today.isoformat())

        self.assertEqual(sorted(result), sorted([edge.id, fresh.id]))

    def test_search_matches_elder_name_email_and_phone(self):
        """
        Aramanın yaşlı adı, başvuru sahibi e-postası ve telefonda çalıştığını doğrular.

        Senaryo:
        - Farklı yaşlı adı, e-posta ve telefonlu talepler oluşturulur.

        Beklenti:
        - Her arama terimi yalnızca ilgili talebi döndürmelidir.
        """
        by_name = make_care_request(elder_full_name='Hatice Demir')
        by_email = make_care_request(applicant=make_user(email='ozel.yakin@example.com'))
        by_phone = make_care_request(contact_phone='05329998877')

        self.assertEqual(self.ids(search='hatice'), [by_name.id])
        self.assertEqual(self.ids(search='ozel.yakin'), [by_email.id])
        self.assertEqual(self.ids(search='5329998877'), [by_phone.id])

    def test_orders_by_preferred_date(self):
        """Tercih edilen tarihe göre artan sıralamanın çalıştığını doğrular."""
        later = make_care_request(preferred_date=timezone.localdate() + timedelta(days=9))
        sooner = make_care_request(preferred_date=timezone.localdate() + timedelta(days=2))

        self.assertEqual(self.ids(ordering='preferred_date'), [sooner.id, later.id])

    def test_invalid_status_filter_is_rejected(self):
        """Geçersiz durum değeriyle filtrelemenin 400 döndürdüğünü doğrular (hata yolu)."""
        response = self.client.get(self.url, {'status': 'unknown'})

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
