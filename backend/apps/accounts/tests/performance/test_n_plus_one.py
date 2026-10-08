from django.db import connection
from django.test.utils import CaptureQueriesContext
from django.urls import reverse
from rest_framework.test import APITestCase

from apps.care.tests.factories import make_care_request, make_service, make_user


class AccountsNPlusOneTests(APITestCase):
    """Hesap uç noktalarının ilişkili kayıt sayısından bağımsız sorgu sayısıyla çalıştığını doğrular."""

    def count_queries(self, url, **params):
        """
        Tek bir GET isteğinin çalıştırdığı SQL sorgusu sayısını ölçer.

        Args:
            url (str): İstek adresi.
            **params (Any): Sorgu parametreleri.

        Returns:
            int: Sorgu sayısı.
        """
        with CaptureQueriesContext(connection) as context:
            response = self.client.get(url, params)
        self.assertEqual(response.status_code, 200)
        return len(context.captured_queries)

    def test_admin_user_list_with_many_requests_has_no_n_plus_one(self):
        """
        Admin kullanıcı listesinde çok başvurusu olan kullanıcıların sorgu sayısını artırmadığını doğrular.

        Senaryo:
        - 1 başvurusu olan 1 kullanıcıyla sorgu ölçülür.
        - Her biri farklı hizmetlerde 5 başvurusu olan 9 kullanıcı daha eklenip tekrar ölçülür.

        Beklenti:
        - Sorgu sayısı değişmemelidir.
        """
        self.client.force_authenticate(make_user(is_staff=True))
        url = reverse('accounts-admin:user-list')
        make_care_request()
        baseline = self.count_queries(url)
        for _index in range(9):
            user = make_user()
            for _request in range(5):
                make_care_request(applicant=user, service=make_service())

        self.assertEqual(self.count_queries(url), baseline)

    def test_admin_user_detail_has_no_n_plus_one(self):
        """
        Admin kullanıcı detayında başvuru sayısının sorgu sayısını artırmadığını doğrular.

        Senaryo:
        - 1 başvurusu olan kullanıcının detayı ölçülür.
        - Aynı kullanıcıya farklı hizmetlerde 9 başvuru daha eklenip tekrar ölçülür.

        Beklenti:
        - Sorgu sayısı değişmemelidir.
        """
        self.client.force_authenticate(make_user(is_staff=True))
        user = make_user()
        make_care_request(applicant=user)
        url = reverse('accounts-admin:user-detail', args=[user.pk])
        baseline = self.count_queries(url)
        for _index in range(9):
            make_care_request(applicant=user, service=make_service())

        self.assertEqual(self.count_queries(url), baseline)

    def test_me_has_no_n_plus_one(self):
        """
        Oturumdaki kullanıcı bilgisi uç noktasının sorgu sayısının kullanıcının başvurularından bağımsız olduğunu doğrular.

        Senaryo:
        - Başvurusu olmayan kullanıcıyla `me/` ölçülür.
        - Kullanıcıya farklı hizmetlerde 10 başvuru eklenip tekrar ölçülür.

        Beklenti:
        - Sorgu sayısı değişmemelidir.
        """
        user = make_user()
        self.client.force_authenticate(user)
        url = reverse('accounts:me')
        baseline = self.count_queries(url)
        for _index in range(10):
            make_care_request(applicant=user, service=make_service())

        self.assertEqual(self.count_queries(url), baseline)
