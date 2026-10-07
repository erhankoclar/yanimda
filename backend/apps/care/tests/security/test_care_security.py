from unittest.mock import patch

from django.core.cache import cache
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework.throttling import SimpleRateThrottle

from apps.care.models import CareRequest
from apps.care.tests.factories import care_request_data, make_care_request, make_service, make_user
from apps.care.throttles import CareRequestCreateRateThrottle


class CareRequestSecurityTests(APITestCase):
    def setUp(self):
        """Throttle sayaçlarını sıfırlar, başvuru sahibi ve hizmet hazırlar."""
        cache.clear()
        self.user = make_user()
        self.service = make_service()

    def payload(self, **overrides):
        """
        Talep oluşturma için geçerli JSON gövdesini döndürür.

        Args:
            **overrides (Any): Varsayılan alanları ezen değerler.

        Returns:
            dict[str, Any]: İstek gövdesi.
        """
        data = care_request_data()
        data['preferred_date'] = data['preferred_date'].isoformat()
        return {**data, 'service': self.service.id, 'consent': True, **overrides}

    def test_anonymous_cannot_list_or_create(self):
        """Kimlik doğrulaması olmadan talep listelenemediğini ve oluşturulamadığını doğrular."""
        url = reverse('care:request-list')

        self.assertEqual(self.client.get(url).status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(self.client.post(url, self.payload(), format='json').status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertFalse(CareRequest.objects.exists())

    def test_other_users_request_is_not_found(self):
        """
        Başka kullanıcının talebine erişimin 404 ile engellendiğini doğrular (IDOR koruması).

        Senaryo:
        - Başka bir kullanıcıya ait talep oluşturulur.
        - Oturumdaki kullanıcı bu talebin detayını ister.

        Beklenti:
        - 404 dönmeli; talebin varlığı açığa çıkmamalıdır.
        """
        foreign = make_care_request()
        self.client.force_authenticate(self.user)

        response = self.client.get(reverse('care:request-detail', args=[foreign.pk]))

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_create_ignores_protected_fields(self):
        """
        Oluşturma isteğindeki korumalı alanların yok sayıldığını doğrular (toplu atama koruması).

        Senaryo:
        - İstek gövdesine `status`, `admin_note` ve başka kullanıcıyı gösteren `applicant` eklenir.

        Beklenti:
        - Talep `new` durumunda, boş notla ve oturumdaki kullanıcı adına oluşmalıdır.
        """
        other = make_user()
        self.client.force_authenticate(self.user)

        response = self.client.post(reverse('care:request-list'), self.payload(
            status=CareRequest.Status.COMPLETED, admin_note='hack', applicant=other.id,
        ), format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        care_request = CareRequest.objects.get()
        self.assertEqual(care_request.status, CareRequest.Status.NEW)
        self.assertEqual(care_request.admin_note, '')
        self.assertEqual(care_request.applicant, self.user)

    def test_admin_note_is_not_exposed_to_applicant(self):
        """Yönetici notunun başvuru sahibine dönen yanıtlarda yer almadığını doğrular (iç bilgi sızıntısı)."""
        care_request = make_care_request(applicant=self.user, admin_note='İç not')
        self.client.force_authenticate(self.user)

        detail = self.client.get(reverse('care:request-detail', args=[care_request.pk]))
        listing = self.client.get(reverse('care:request-list'))

        self.assertNotIn('admin_note', detail.data)
        self.assertNotIn('admin_note', listing.data['results'][0])
        self.assertNotIn('applicant', detail.data)

    def test_applicant_cannot_update_or_delete(self):
        """
        Başvuru sahibinin talebini güncelleyemediğini ve silemediğini doğrular.

        Senaryo:
        - Kullanıcı kendi talebine PATCH, PUT ve DELETE gönderir.

        Beklenti:
        - Hepsi 405 dönmeli ve talep değişmemelidir.
        """
        care_request = make_care_request(applicant=self.user)
        self.client.force_authenticate(self.user)
        url = reverse('care:request-detail', args=[care_request.pk])

        for method in (self.client.patch, self.client.put, self.client.delete):
            self.assertEqual(method(url, {'status': 'completed'}).status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        care_request.refresh_from_db()
        self.assertEqual(care_request.status, CareRequest.Status.NEW)

    def test_create_is_throttled_per_user(self):
        """
        Talep oluşturmanın kullanıcı başına sınırlandığını, listelemenin etkilenmediğini doğrular.

        Senaryo:
        - Oluşturma oranı 1/gün yapılır, iki talep gönderilir ve liste çağrılır.

        Beklenti:
        - İkinci oluşturma 429 dönmeli; liste isteği 200 dönmelidir.
        """
        self.client.force_authenticate(self.user)
        url = reverse('care:request-list')
        with patch.dict(SimpleRateThrottle.THROTTLE_RATES, {CareRequestCreateRateThrottle.scope: '1/day'}):
            first = self.client.post(url, self.payload(), format='json')
            second = self.client.post(url, self.payload(), format='json')
            listing = self.client.get(url)

        self.assertEqual(first.status_code, status.HTTP_201_CREATED)
        self.assertEqual(second.status_code, status.HTTP_429_TOO_MANY_REQUESTS)
        self.assertEqual(listing.status_code, status.HTTP_200_OK)

    def test_service_list_is_read_only(self):
        """Herkese açık hizmet listesine yazma isteklerinin kapalı olduğunu doğrular."""
        self.client.force_authenticate(self.user)

        response = self.client.post(reverse('care:service-list'), {'name': 'X'})

        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
