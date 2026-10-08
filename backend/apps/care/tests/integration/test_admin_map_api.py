from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from apps.care.factories import CareRequestFactory, ServiceInquiryFactory, ServiceTypeFactory
from apps.care.tests.factories import make_user
from apps.care.tests.map_data import build_dataset, days_ago


class AdminMapApiTests(APITestCase):
    """Admin harita endpoint'inin yanıt değerlerini, parametrelerini ve dil desteğini doğrular."""

    def setUp(self):
        """Admin olarak oturum açar ve küçük veri kümesini kurar."""
        self.client.force_authenticate(make_user(is_staff=True))
        self.data = build_dataset()
        self.url = reverse('care-admin:map')

    def test_shape_and_values(self):
        """
        Yanıtın şeklini ve sayım değerlerini doğrular.

        Senaryo:
        - Küçük veri kümesiyle harita endpoint'i çağrılır.

        Beklenti:
        - 200 döner; toplam, ilçe ve mahalle sayıları veri kümesiyle uyuşmalıdır.
        """
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['total'], 5)
        districts = {item['id']: item for item in response.data['districts']}
        self.assertEqual(districts[self.data.d1.id]['count'], 4)
        self.assertEqual(districts[self.data.d1.id]['osm_id'], self.data.d1.osm_id)
        self.assertEqual(districts[self.data.d3.id]['count'], 0)
        neighborhoods = response.data['neighborhoods']
        self.assertEqual(neighborhoods[0]['id'], self.data.n1.id)
        self.assertEqual(len(neighborhoods), 3)
        self.assertEqual(neighborhoods[0]['by_service'], {str(self.data.s1.id): 3})

    def test_source_param(self):
        """
        source parametresinin sayımı kaynağa göre daralttığını doğrular.

        Senaryo:
        - source=inquiries ve source=requests ile çağrılır.

        Beklenti:
        - Toplamlar sırasıyla 3 ve 2 olmalıdır.
        """
        self.assertEqual(self.client.get(self.url, {'source': 'inquiries'}).data['total'], 3)
        self.assertEqual(self.client.get(self.url, {'source': 'requests'}).data['total'], 2)

    def test_days_param(self):
        """
        days parametresinin eski kayıtları dışladığını doğrular.

        Senaryo:
        - 100 gün önceki iki talep eklenir; days=30, 90 ve 365 ile çağrılır.

        Beklenti:
        - 30 ve 90 günde eski kayıtlar yoktur (5); 365 günde vardır (7).
        """
        ServiceInquiryFactory(service=self.data.s1, neighborhood=self.data.n3, created_at=days_ago(100))
        CareRequestFactory(service=self.data.s1, neighborhood=self.data.n3, created_at=days_ago(100))

        self.assertEqual(self.client.get(self.url, {'days': 30}).data['total'], 5)
        self.assertEqual(self.client.get(self.url, {'days': 90}).data['total'], 5)
        self.assertEqual(self.client.get(self.url, {'days': 365}).data['total'], 7)

    def test_invalid_source_returns_field_error(self):
        """
        Geçersiz source değerinin 400 ve alan hatası döndürdüğünü doğrular.

        Senaryo:
        - source=bogus ile çağrılır.

        Beklenti:
        - 400 ve yanıtta `source` alanı hatası bulunmalıdır.
        """
        response = self.client.get(self.url, {'source': 'bogus'})

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('source', response.data)

    def test_invalid_days_returns_field_error(self):
        """
        Geçersiz days değerlerinin 400 ve alan hatası döndürdüğünü doğrular.

        Senaryo:
        - days=7 ve days=abc ile çağrılır.

        Beklenti:
        - Her ikisi de 400 ve `days` alanı hatası vermelidir.
        """
        for value in ('7', 'abc'):
            with self.subTest(days=value):
                response = self.client.get(self.url, {'days': value})

                self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
                self.assertIn('days', response.data)

    def test_service_names_follow_accept_language(self):
        """
        Hizmet adlarının Accept-Language başlığına uyduğunu doğrular.

        Senaryo:
        - Bir hizmete İngilizce çeviri eklenir; Türkçe ve İngilizce istek yapılır.

        Beklenti:
        - İngilizce istekte İngilizce ad, Türkçe istekte Türkçe ad dönmeli; çevirisiz hizmet Türkçe kalmalıdır.
        """
        service = self.data.s1
        service.set_current_language('en')
        service.name = 'Companionship'
        service.description = 'Regular visits'
        service.save()

        def names(language):
            data = self.client.get(self.url, HTTP_ACCEPT_LANGUAGE=language).data
            return {item['id']: item['name'] for item in data['services']}

        self.assertEqual(names('en')[service.id], 'Companionship')
        self.assertEqual(names('en')[self.data.s2.id], 'Küçük tamir')
        self.assertEqual(names('tr')[service.id], 'Refakat')

    def test_inactive_service_not_listed(self):
        """
        Pasif hizmetin services listesinde yer almadığını doğrular.

        Senaryo:
        - Pasif bir hizmet oluşturulur.

        Beklenti:
        - Hizmet listede bulunmamalıdır.
        """
        inactive = ServiceTypeFactory(is_active=False)

        ids = [item['id'] for item in self.client.get(self.url).data['services']]

        self.assertNotIn(inactive.id, ids)


class AdminInquiryDateFilterTests(APITestCase):
    """Admin hızlı talep listesinin created_from / created_to süzgeçlerini doğrular."""

    def setUp(self):
        """Üç farklı günde hızlı talep oluşturur."""
        self.client.force_authenticate(make_user(is_staff=True))
        self.service = ServiceTypeFactory()
        self.old = ServiceInquiryFactory(service=self.service, created_at=days_ago(20))
        self.middle = ServiceInquiryFactory(service=self.service, created_at=days_ago(10))
        self.recent = ServiceInquiryFactory(service=self.service, created_at=days_ago(1))
        self.url = reverse('care-admin:inquiry-list')

    def ids(self, **params):
        """
        Süzgeçle listelenen kimlikleri döndürür.

        Args:
            **params (Any): Sorgu parametreleri.

        Returns:
            set[int]: Satır kimlikleri.
        """
        return {row['id'] for row in self.client.get(self.url, params).data['results']}

    def test_created_from(self):
        """
        created_from süzgecinin başlangıç gününü dahil ettiğini doğrular.

        Senaryo:
        - created_from olarak orta kaydın günü verilir.

        Beklenti:
        - Orta ve yeni kayıt döner, eski kayıt dönmez.
        """
        day = days_ago(10).date().isoformat()

        self.assertEqual(self.ids(created_from=day), {self.middle.id, self.recent.id})

    def test_created_to(self):
        """
        created_to süzgecinin bitiş gününü dahil ettiğini doğrular.

        Senaryo:
        - created_to olarak orta kaydın günü verilir.

        Beklenti:
        - Eski ve orta kayıt döner, yeni kayıt dönmez.
        """
        day = days_ago(10).date().isoformat()

        self.assertEqual(self.ids(created_to=day), {self.old.id, self.middle.id})

    def test_created_range(self):
        """
        İki süzgecin birlikte aralık oluşturduğunu doğrular.

        Senaryo:
        - Her iki sınır orta kaydın günü olarak verilir.

        Beklenti:
        - Yalnızca orta kayıt dönmelidir.
        """
        day = days_ago(10).date().isoformat()

        self.assertEqual(self.ids(created_from=day, created_to=day), {self.middle.id})
