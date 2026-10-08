from django.urls import reverse
from rest_framework.test import APITestCase


class GeoSecurityTests(APITestCase):
    def test_endpoints_reachable_anonymously(self):
        """
        Uç noktaların oturum açmadan erişilebildiğini doğrular.

        Senaryo:
        - Kimlik bilgisi olmayan istemciyle iki liste adresi istenir.

        Beklenti:
        - Her ikisi de 200 dönmelidir.
        """
        self.assertEqual(self.client.get(reverse('geo:district-list')).status_code, 200)
        self.assertEqual(self.client.get(reverse('geo:neighborhood-list', args=[1])).status_code, 200)

    def test_only_get_is_allowed(self):
        """
        Uç noktalarda GET dışındaki metotların reddedildiğini doğrular.

        Senaryo:
        - Her iki adrese POST, PUT, PATCH ve DELETE istekleri gönderilir.

        Beklenti:
        - Tüm istekler 405 dönmelidir.
        """
        urls = [reverse('geo:district-list'), reverse('geo:neighborhood-list', args=[1])]
        for url in urls:
            for method in ('post', 'put', 'patch', 'delete'):
                response = getattr(self.client, method)(url, {}, format='json')
                self.assertEqual(response.status_code, 405, f'{method} {url}')

    def test_non_integer_district_id_is_404(self):
        """
        Tam sayı olmayan ilçe kimliğinin 404 döndürdüğünü doğrular.

        Senaryo:
        - Yol parametresine metin verilerek mahalle adresi istenir.

        Beklenti:
        - 404 durum kodu dönmelidir.
        """
        response = self.client.get('/api/geo/districts/abc/neighborhoods/')

        self.assertEqual(response.status_code, 404)
