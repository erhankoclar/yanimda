from django.core.cache import cache
from django.urls import reverse
from django.utils.translation import gettext
from rest_framework import status
from rest_framework.test import APITestCase

from apps.care.factories import ServiceInquiryFactory
from apps.care.models import CareRequest, ServiceInquiry
from apps.care.tests.factories import care_request_data, make_care_request, make_service, make_user
from apps.geo.factories import DistrictFactory, NeighborhoodFactory


class LocationCreateApiTests(APITestCase):
    """Başvuru ve hızlı talep oluştururken mahalle alanının doğrulanıp `location` olarak döndüğünü sınar."""

    def setUp(self):
        """Throttle sayaçlarını sıfırlar; hizmet, ilçe ve mahalle hazırlar."""
        cache.clear()
        self.service = make_service()
        self.district = DistrictFactory(name='Kadıköy')
        self.neighborhood = NeighborhoodFactory(district=self.district, name='Caferağa Mahallesi')
        self.client.force_authenticate(make_user())

    def request_payload(self, **overrides):
        """
        Başvuru oluşturma için geçerli gövdeyi döndürür.

        Args:
            **overrides (Any): Varsayılan alanları ezen değerler.

        Returns:
            dict[str, Any]: İstek gövdesi.
        """
        data = care_request_data()
        data['preferred_date'] = data['preferred_date'].isoformat()
        data['neighborhood'] = self.neighborhood.pk
        return {**data, 'service': self.service.id, 'consent': True, **overrides}

    def inquiry_payload(self, **overrides):
        """
        Hızlı talep için geçerli gövdeyi döndürür.

        Args:
            **overrides (Any): Varsayılan alanları ezen değerler.

        Returns:
            dict[str, Any]: İstek gövdesi.
        """
        return {
            'full_name': 'Deneme Kişi', 'email': 'deneme@example.com', 'service': self.service.id,
            'neighborhood': self.neighborhood.pk, 'consent': True, 'website': '',
            'message': 'Annem için haftada iki gün refakat desteği istiyoruz.', **overrides,
        }

    def test_request_response_contains_location(self):
        """
        Başvuru yanıtının ilçe ve mahalle adlarını `location` altında döndürdüğünü doğrular.

        Senaryo:
        - Geçerli bir mahalle kimliğiyle başvuru oluşturulur.

        Beklenti:
        - 201 dönmeli; `location` ilçe ve mahalle için kimlik, ad ve osm_id içermeli, `neighborhood` yanıtta olmamalıdır.
        """
        response = self.client.post(reverse('care:request-list'), self.request_payload(), format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)
        self.assertEqual(response.data['location'], {
            'district': {'id': self.district.id, 'name': 'Kadıköy', 'osm_id': self.district.osm_id},
            'neighborhood': {
                'id': self.neighborhood.id, 'name': 'Caferağa Mahallesi', 'osm_id': self.neighborhood.osm_id,
            },
        })
        self.assertNotIn('neighborhood', response.data)
        self.assertEqual(CareRequest.objects.get(pk=response.data['id']).neighborhood, self.neighborhood)

    def test_request_requires_neighborhood(self):
        """
        Mahalle verilmeden başvurunun reddedildiğini doğrular (hata yolu).

        Senaryo:
        - Mahalle alanı gövdeden çıkarılarak başvuru gönderilir.

        Beklenti:
        - 400 dönmeli, `neighborhood` alanında zorunluluk hatası olmalı ve kayıt oluşmamalıdır.
        """
        payload = self.request_payload()
        del payload['neighborhood']

        response = self.client.post(reverse('care:request-list'), payload, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['neighborhood'], [gettext('This field is required.')])
        self.assertFalse(CareRequest.objects.exists())

    def test_request_rejects_unknown_neighborhood(self):
        """
        Var olmayan mahalle kimliğiyle başvurunun reddedildiğini doğrular (hata yolu).

        Senaryo:
        - Veritabanında olmayan bir mahalle kimliği gönderilir.

        Beklenti:
        - 400 dönmeli, `neighborhood` alanında hata olmalı ve kayıt oluşmamalıdır.
        """
        response = self.client.post(
            reverse('care:request-list'), self.request_payload(neighborhood=999999999), format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('neighborhood', response.data)
        self.assertFalse(CareRequest.objects.exists())

    def test_inquiry_response_contains_location(self):
        """
        Hızlı talep yanıtının ilçe ve mahalle adlarını `location` altında döndürdüğünü doğrular.

        Senaryo:
        - Kimlik doğrulamasız geçerli bir mahalle kimliğiyle hızlı talep gönderilir.

        Beklenti:
        - 201 dönmeli; `location` ilçe ve mahalle adlarını içermeli, kayıt mahalleye bağlanmalıdır.
        """
        self.client.force_authenticate(None)

        response = self.client.post(reverse('care:inquiry-create'), self.inquiry_payload(), format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)
        self.assertEqual(response.data['location']['district']['name'], 'Kadıköy')
        self.assertEqual(response.data['location']['neighborhood']['name'], 'Caferağa Mahallesi')
        self.assertNotIn('neighborhood', response.data)
        self.assertEqual(ServiceInquiry.objects.get(pk=response.data['id']).neighborhood, self.neighborhood)

    def test_inquiry_requires_neighborhood(self):
        """
        Mahalle verilmeden hızlı talebin reddedildiğini doğrular (hata yolu).

        Senaryo:
        - Mahalle alanı olmadan hızlı talep gönderilir.

        Beklenti:
        - 400 dönmeli, `neighborhood` alanında zorunluluk hatası olmalı ve kayıt oluşmamalıdır.
        """
        payload = self.inquiry_payload()
        del payload['neighborhood']

        response = self.client.post(reverse('care:inquiry-create'), payload, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['neighborhood'], [gettext('This field is required.')])
        self.assertFalse(ServiceInquiry.objects.exists())

    def test_inquiry_rejects_unknown_neighborhood(self):
        """
        Var olmayan mahalle kimliğiyle hızlı talebin reddedildiğini doğrular (hata yolu).

        Senaryo:
        - Veritabanında olmayan bir mahalle kimliği gönderilir.

        Beklenti:
        - 400 dönmeli, `neighborhood` alanında hata olmalı ve kayıt oluşmamalıdır.
        """
        response = self.client.post(
            reverse('care:inquiry-create'), self.inquiry_payload(neighborhood=999999999), format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('neighborhood', response.data)
        self.assertFalse(ServiceInquiry.objects.exists())


class AdminLocationFilterApiTests(APITestCase):
    """Admin başvuru ve hızlı talep listelerinin konuma göre süzüldüğünü ve arandığını sınar."""

    def setUp(self):
        """İki ilçede üç mahalle ve admin oturumu hazırlar."""
        self.client.force_authenticate(make_user(is_staff=True))
        self.kadikoy = DistrictFactory(name='Kadıköy')
        self.uskudar = DistrictFactory(name='Üsküdar')
        self.moda = NeighborhoodFactory(district=self.kadikoy, name='Moda Mahallesi')
        self.fenerbahce = NeighborhoodFactory(district=self.kadikoy, name='Fenerbahçe Mahallesi')
        self.altunizade = NeighborhoodFactory(district=self.uskudar, name='Altunizade Mahallesi')

    def ids(self, name, **params):
        """
        Verilen admin liste adresini parametrelerle çağırıp kimlikleri döndürür.

        Args:
            name (str): `care-admin` ad alanındaki rota adı.
            **params (Any): Sorgu parametreleri.

        Returns:
            set[int]: Dönen kayıt kimlikleri.
        """
        response = self.client.get(reverse(f'care-admin:{name}'), params)
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        return {row['id'] for row in response.data['results']}

    def test_request_list_filters_by_district_and_neighborhood(self):
        """
        Admin başvuru listesinin `district` ve `neighborhood` parametreleriyle süzüldüğünü doğrular.

        Senaryo:
        - Kadıköy'de iki, Üsküdar'da bir başvuru oluşturulur.
        - Liste önce ilçeyle, sonra mahalleyle, sonra ikisinin çelişen birleşimiyle çağrılır.

        Beklenti:
        - İlçe süzgeci ilçedeki tüm, mahalle süzgeci yalnızca o mahalledeki başvuruları döndürmelidir.
        """
        moda = make_care_request(neighborhood=self.moda)
        fener = make_care_request(neighborhood=self.fenerbahce)
        uskudar = make_care_request(neighborhood=self.altunizade)

        self.assertEqual(self.ids('request-list', district=self.kadikoy.id), {moda.id, fener.id})
        self.assertEqual(self.ids('request-list', district=self.uskudar.id), {uskudar.id})
        self.assertEqual(self.ids('request-list', neighborhood=self.moda.id), {moda.id})
        self.assertEqual(self.ids('request-list', district=self.uskudar.id, neighborhood=self.moda.id), set())

    def test_request_list_returns_location(self):
        """
        Admin başvuru satırının `location` ve eski kayıtta `null` döndürdüğünü doğrular.

        Senaryo:
        - Biri mahalleli, biri mahallesiz (eski) iki başvuru oluşturulur.

        Beklenti:
        - Mahalleli satırda ilçe ve mahalle adı, eski satırda `location` null olmalıdır.
        """
        located = make_care_request(neighborhood=self.moda)
        old = make_care_request(neighborhood=None)

        rows = {row['id']: row for row in self.client.get(reverse('care-admin:request-list')).data['results']}

        self.assertEqual(rows[located.id]['location']['neighborhood']['name'], 'Moda Mahallesi')
        self.assertEqual(rows[located.id]['location']['district']['name'], 'Kadıköy')
        self.assertIsNone(rows[old.id]['location'])

    def test_request_search_matches_neighborhood_and_district_names(self):
        """
        Admin başvuru aramasının mahalle ve ilçe adlarıyla eşleştiğini doğrular.

        Senaryo:
        - Farklı konumlarda üç başvuru oluşturulur.
        - Mahalle adı ve ilçe adı ile arama yapılır.

        Beklenti:
        - Mahalle adı yalnızca o başvuruyu, ilçe adı ilçedeki tüm başvuruları döndürmelidir.
        """
        moda = make_care_request(neighborhood=self.moda)
        fener = make_care_request(neighborhood=self.fenerbahce)
        make_care_request(neighborhood=self.altunizade)

        self.assertEqual(self.ids('request-list', search='Moda'), {moda.id})
        self.assertEqual(self.ids('request-list', search='Kadıköy'), {moda.id, fener.id})

    def test_inquiry_list_filters_by_service_district_and_neighborhood(self):
        """
        Admin hızlı talep listesinin `service`, `district` ve `neighborhood` ile süzüldüğünü doğrular.

        Senaryo:
        - İki hizmet ve üç konuma dağılmış üç hızlı talep oluşturulur.
        - Liste her süzgeçle ayrı ayrı çağrılır.

        Beklenti:
        - Her süzgeç yalnızca eşleşen talepleri döndürmelidir.
        """
        service_a, service_b = make_service(), make_service()
        first = ServiceInquiryFactory(service=service_a, neighborhood=self.moda)
        second = ServiceInquiryFactory(service=service_b, neighborhood=self.fenerbahce)
        third = ServiceInquiryFactory(service=service_a, neighborhood=self.altunizade)

        self.assertEqual(self.ids('inquiry-list', district=self.kadikoy.id), {first.id, second.id})
        self.assertEqual(self.ids('inquiry-list', neighborhood=self.altunizade.id), {third.id})
        self.assertEqual(self.ids('inquiry-list', service=service_a.id), {first.id, third.id})
        self.assertEqual(self.ids('inquiry-list', service=service_a.id, district=self.kadikoy.id), {first.id})

    def test_inquiry_list_returns_location(self):
        """
        Admin hızlı talep satırının `location` ve eski kayıtta `null` döndürdüğünü doğrular.

        Senaryo:
        - Biri mahalleli, biri mahallesiz iki hızlı talep oluşturulur.

        Beklenti:
        - Mahalleli satırda ilçe ve mahalle adı, eski satırda `location` null olmalıdır.
        """
        located = ServiceInquiryFactory(neighborhood=self.altunizade)
        old = ServiceInquiryFactory(neighborhood=None)

        rows = {row['id']: row for row in self.client.get(reverse('care-admin:inquiry-list')).data['results']}

        self.assertEqual(rows[located.id]['location']['district']['name'], 'Üsküdar')
        self.assertIsNone(rows[old.id]['location'])
