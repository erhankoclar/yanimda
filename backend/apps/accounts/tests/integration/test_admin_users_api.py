from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from apps.care.tests.factories import make_care_request, make_user


class AdminUserApiTests(APITestCase):
    def setUp(self):
        """Admin kullanıcıyla oturum açar."""
        self.admin = make_user(is_staff=True, email='yonetici@example.com')
        self.client.force_authenticate(self.admin)
        self.url = reverse('accounts-admin:user-list')

    def results(self, **params):
        """
        Admin kullanıcı listesini parametrelerle çağırır.

        Args:
            **params (Any): Sorgu parametreleri.

        Returns:
            list[dict[str, Any]]: Sonuç satırları.
        """
        response = self.client.get(self.url, params)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        return response.data['results']

    def test_lists_users_with_request_counts(self):
        """
        Kullanıcıların talep sayılarıyla listelendiğini doğrular.

        Senaryo:
        - İki talebi olan bir başvuru sahibi oluşturulur.

        Beklenti:
        - Başvuru sahibinin satırında `request_count` 2, admin satırında 0 olmalıdır.
        """
        applicant = make_user()
        make_care_request(applicant=applicant)
        make_care_request(applicant=applicant)

        counts = {row['id']: row['request_count'] for row in self.results()}

        self.assertEqual(counts[applicant.id], 2)
        self.assertEqual(counts[self.admin.id], 0)

    def test_filters_by_admin_right_and_active_state(self):
        """
        Admin yetkisi ve aktiflik filtrelerinin çalıştığını doğrular.

        Senaryo:
        - Bir aktif ve bir pasif standart kullanıcı oluşturulur.

        Beklenti:
        - `is_staff=true` yalnızca admini, `is_active=false` yalnızca pasif kullanıcıyı döndürmelidir.
        """
        make_user()
        passive = make_user(is_active=False)

        self.assertEqual([row['id'] for row in self.results(is_staff='true')], [self.admin.id])
        self.assertEqual([row['id'] for row in self.results(is_active='false')], [passive.id])

    def test_search_by_name_and_phone(self):
        """Ad ve telefona göre aramanın ilgili kullanıcıyı bulduğunu doğrular."""
        by_name = make_user(first_name='Zeynep')
        by_phone = make_user(phone='05321234567')

        self.assertEqual([row['id'] for row in self.results(search='zeynep')], [by_name.id])
        self.assertEqual([row['id'] for row in self.results(search='5321234567')], [by_phone.id])

    def test_orders_by_request_count(self):
        """Talep sayısına göre azalan sıralamanın çalıştığını doğrular."""
        busy = make_user()
        make_care_request(applicant=busy)

        rows = self.results(ordering='-request_count')

        self.assertEqual(rows[0]['id'], busy.id)

    def test_detail_returns_user(self):
        """
        Kullanıcı detayının talep sayısıyla döndüğünü doğrular.

        Senaryo:
        - Bir talebi olan kullanıcının detayı istenir.

        Beklenti:
        - 200 dönmeli; e-posta ve `request_count` doğru olmalıdır.
        """
        applicant = make_user()
        make_care_request(applicant=applicant)

        response = self.client.get(reverse('accounts-admin:user-detail', args=[applicant.pk]))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['email'], applicant.email)
        self.assertEqual(response.data['request_count'], 1)
