from django.urls import reverse
from django.utils.translation import gettext
from rest_framework import status
from rest_framework.test import APITestCase

from apps.care.models import CareRequest
from apps.care.tests.factories import make_care_request, make_user


class AdminRequestDetailApiTests(APITestCase):
    def setUp(self):
        """Admin kullanıcıyla oturum açar ve bir talep hazırlar."""
        self.client.force_authenticate(make_user(is_staff=True))
        self.care_request = make_care_request(admin_note='İlk not')
        self.url = reverse('care-admin:request-detail', args=[self.care_request.pk])

    def test_detail_includes_internal_fields(self):
        """
        Admin detayının yönetici notu ve geçilebilir durumları içerdiğini doğrular.

        Senaryo:
        - `new` durumundaki talebin detayı istenir.

        Beklenti:
        - 200 dönmeli; not, adres ve `next_statuses` doğru olmalıdır.
        """
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['admin_note'], 'İlk not')
        self.assertEqual(response.data['address'], self.care_request.address)
        self.assertEqual(response.data['next_statuses'], ['reviewing', 'cancelled'])

    def test_moves_status_forward_and_updates_note(self):
        """
        Durumun bir sonraki adıma taşınıp notun güncellendiğini doğrular.

        Senaryo:
        - `new` talep `reviewing` durumuna ve yeni notla PATCH edilir.

        Beklenti:
        - 200 dönmeli; durum, not ve yeni `next_statuses` güncel olmalıdır.
        """
        response = self.client.patch(self.url, {'status': 'reviewing', 'admin_note': 'Arandı'}, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.care_request.refresh_from_db()
        self.assertEqual(self.care_request.status, CareRequest.Status.REVIEWING)
        self.assertEqual(self.care_request.admin_note, 'Arandı')
        self.assertEqual(response.data['next_statuses'], ['assigned', 'cancelled'])

    def test_note_only_update_keeps_status(self):
        """Yalnızca not gönderildiğinde durumun değişmediğini doğrular."""
        response = self.client.patch(self.url, {'admin_note': 'Yalnız not'}, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.care_request.refresh_from_db()
        self.assertEqual(self.care_request.status, CareRequest.Status.NEW)
        self.assertEqual(self.care_request.admin_note, 'Yalnız not')

    def test_rejects_invalid_transition(self):
        """
        İzin verilmeyen durum geçişinin çevrilmiş hata ile reddedildiğini doğrular (hata yolu).

        Senaryo:
        - `new` talep doğrudan `completed` durumuna taşınmak istenir.

        Beklenti:
        - 400 dönmeli, hata mevcut ve hedef durum etiketlerini içermeli, durum değişmemelidir.
        """
        response = self.client.patch(self.url, {'status': 'completed'}, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        expected = gettext('A request in "%(current)s" status cannot be moved to "%(target)s".') % {
            'current': CareRequest.Status.NEW.label, 'target': CareRequest.Status.COMPLETED.label,
        }
        self.assertEqual(response.data['status'], [expected])
        self.care_request.refresh_from_db()
        self.assertEqual(self.care_request.status, CareRequest.Status.NEW)

    def test_unknown_request_returns_404(self):
        """Olmayan talep kimliği için 404 döndüğünü doğrular."""
        response = self.client.get(reverse('care-admin:request-detail', args=[self.care_request.pk + 999]))

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
