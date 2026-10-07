from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from apps.care.tests.factories import make_care_request, make_user


class AdminRequestUpdateSecurityTests(APITestCase):
    def setUp(self):
        """Admin kullanıcı ve başka bir kullanıcıya ait talep hazırlar."""
        self.owner = make_user()
        self.care_request = make_care_request(applicant=self.owner)
        self.url = reverse('care-admin:request-detail', args=[self.care_request.pk])

    def test_admin_cannot_change_applicant_data(self):
        """
        Admin güncellemesinin başvuru verilerini değiştiremediğini doğrular (toplu atama koruması).

        Senaryo:
        - Admin; yaşlı adı, telefon, adres ve başvuru sahibini değiştiren bir PATCH gönderir.

        Beklenti:
        - İstek kabul edilse de bu alanlar değişmemelidir.
        """
        self.client.force_authenticate(make_user(is_staff=True))
        other = make_user()

        self.client.patch(self.url, {
            'elder_full_name': 'Değişti', 'contact_phone': '05000000000', 'address': 'Başka adres',
            'applicant': other.id, 'consent_given_at': '2000-01-01T00:00:00Z',
        }, format='json')

        self.care_request.refresh_from_db()
        self.assertEqual(self.care_request.elder_full_name, 'Fatma Yılmaz')
        self.assertEqual(self.care_request.contact_phone, '05551112233')
        self.assertEqual(self.care_request.applicant, self.owner)

    def test_applicant_cannot_use_admin_update(self):
        """
        Talep sahibinin bile admin endpoint'iyle kendi talebinin durumunu değiştiremediğini doğrular.

        Senaryo:
        - Talep sahibi admin detay adresine durum PATCH eder.

        Beklenti:
        - 403 dönmeli ve durum değişmemelidir.
        """
        self.client.force_authenticate(self.owner)

        response = self.client.patch(self.url, {'status': 'reviewing'}, format='json')

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.care_request.refresh_from_db()
        self.assertEqual(self.care_request.status, 'new')

    def test_put_and_delete_are_not_allowed(self):
        """Admin talep detayında PUT ve DELETE metotlarının kapalı olduğunu doğrular (kayıt silme koruması)."""
        self.client.force_authenticate(make_user(is_staff=True))

        self.assertEqual(self.client.put(self.url, {}).status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        self.assertEqual(self.client.delete(self.url).status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        self.assertTrue(type(self.care_request).objects.filter(pk=self.care_request.pk).exists())

    def test_admin_note_length_is_limited(self):
        """Yönetici notunun 2000 karakter sınırını aşamadığını doğrular (aşırı veri girişi)."""
        self.client.force_authenticate(make_user(is_staff=True))

        response = self.client.patch(self.url, {'admin_note': 'x' * 2001}, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('admin_note', response.data)
