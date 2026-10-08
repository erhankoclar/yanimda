from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from apps.care.factories import ServiceInquiryFactory
from apps.care.tests.factories import make_user


class AdminInquiryDetailAccessTests(APITestCase):
    def setUp(self):
        """Bir hızlı talep ve detay adresi hazırlar."""
        self.inquiry = ServiceInquiryFactory()
        self.url = reverse('care-admin:inquiry-detail', args=[self.inquiry.pk])

    def test_anonymous_gets_401(self):
        """
        Kimliksiz isteğin hızlı talep detayına erişemediğini doğrular (kişisel veri koruması).

        Senaryo:
        - Oturum açmadan detay adresi çağrılır.

        Beklenti:
        - 401 dönmeli ve yanıt talep verisini içermemelidir.
        """
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertNotIn(self.inquiry.email, str(response.content))

    def test_applicant_gets_403(self):
        """
        Standart kullanıcının başkasının hızlı talebini okuyamadığını doğrular (yetki kontrolü).

        Senaryo:
        - Standart kullanıcı oturum açar ve detay adresini çağırır.

        Beklenti:
        - 403 dönmeli ve e-posta yanıtta yer almamalıdır.
        """
        self.client.force_authenticate(make_user())

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertNotIn(self.inquiry.email, str(response.content))

    def test_only_get_is_allowed_for_admin(self):
        """
        Yönetici için bile yalnızca GET'in açık olduğunu doğrular (veri bütünlüğü).

        Senaryo:
        - Yönetici POST, PUT, PATCH ve DELETE ile detay adresini çağırır.

        Beklenti:
        - Hepsi 405 dönmeli, talep silinmemeli ve değişmemelidir.
        """
        self.client.force_authenticate(make_user(is_staff=True))

        for method in ('post', 'put', 'patch', 'delete'):
            with self.subTest(method=method):
                response = getattr(self.client, method)(self.url, {'full_name': 'Değişti'}, format='json')
                self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        self.inquiry.refresh_from_db()
        self.assertNotEqual(self.inquiry.full_name, 'Değişti')

    def test_detail_exposes_only_defined_fields(self):
        """
        Yanıtın yalnızca tanımlı alanları döndürdüğünü doğrular (fazla veri sızmaz).

        Senaryo:
        - Yönetici detay adresini çağırır.

        Beklenti:
        - Yanıt anahtarları serileştiricinin alan listesiyle birebir aynı olmalıdır.
        """
        self.client.force_authenticate(make_user(is_staff=True))

        response = self.client.get(self.url)

        self.assertEqual(
            set(response.data),
            {'id', 'full_name', 'email', 'service', 'location', 'message', 'consent_given_at', 'created_at'},
        )
