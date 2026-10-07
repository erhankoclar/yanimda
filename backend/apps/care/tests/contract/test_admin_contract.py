from django.urls import reverse
from rest_framework.test import APITestCase

from apps.care.tests.factories import make_care_request, make_user

ADMIN_ROW_FIELDS = {
    'id', 'applicant', 'service', 'elder_full_name', 'elder_age', 'city', 'district',
    'preferred_date', 'time_slot', 'time_slot_display', 'contact_phone', 'status', 'status_display', 'created_at',
}


class AdminResponseContractTests(APITestCase):
    """Admin panelin tablolarının bağlı olduğu yanıt şekillerini sabitler."""

    def setUp(self):
        """Admin kullanıcıyla oturum açar."""
        self.client.force_authenticate(make_user(is_staff=True))

    def test_admin_request_row_fields(self):
        """
        Admin talep tablosu satırının alan kümesini doğrular.

        Senaryo:
        - Bir talep oluşturulur ve admin listesi çağrılır.

        Beklenti:
        - Satır alanları sabit kümeyle; başvuru sahibi ve hizmet alt alanları beklenen kümelerle eşleşmelidir.
        """
        make_care_request()

        data = self.client.get(reverse('care-admin:request-list')).data

        self.assertEqual(set(data), {'count', 'next', 'previous', 'results'})
        row = data['results'][0]
        self.assertEqual(set(row), ADMIN_ROW_FIELDS)
        self.assertEqual(set(row['applicant']), {'id', 'email', 'full_name', 'phone'})
        self.assertEqual(set(row['service']), {'id', 'name', 'slug', 'description', 'icon'})
