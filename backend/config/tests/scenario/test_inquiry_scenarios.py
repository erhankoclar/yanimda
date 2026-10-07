from rest_framework.test import APIClient

from apps.care.models import ServiceInquiry
from config.tests.scenario.base import ScenarioTestCase


class QuickInquiryScenarioTests(ScenarioTestCase):
    def test_visitor_inquiry_is_stored_and_visible_to_admin(self):
        """
        Hesabı olmayan ziyaretçinin hızlı talebinin kalıcı saklanıp yöneticiye ulaştığını doğrular.

        Senaryo:
        - Ziyaretçi hizmet listesinden bir hizmet seçip formu gönderir.
        - Yönetici hızlı talepler listesine bakar.

        Beklenti:
        - Yanıt kayıt kimliğini içermeli; aynı kayıt veritabanında ve admin listesinde bulunmalıdır.
        """
        visitor = APIClient()
        service_id = visitor.get('/api/services/').data[0]['id']

        response = visitor.post('/api/inquiries/', {
            'full_name': 'Deneme Kişi', 'email': 'ziyaretci@example.com', 'service': service_id,
            'message': 'Babam için hastane randevusuna eşlik istiyoruz.', 'consent': True, 'website': '',
        }, format='json')

        self.assertEqual(response.status_code, 201)
        self.assertTrue(ServiceInquiry.objects.filter(pk=response.data['id'], email='ziyaretci@example.com').exists())
        admin_rows = self.admin.get('/api/admin/inquiries/').data['results']
        self.assertEqual([row['id'] for row in admin_rows], [response.data['id']])

    def test_failed_inquiry_leaves_no_record(self):
        """
        Doğrulamadan geçemeyen talebin hiçbir kayıt bırakmadığını doğrular.

        Senaryo:
        - Ziyaretçi onay vermeden formu gönderir.

        Beklenti:
        - 400 dönmeli ve veritabanında talep olmamalıdır; başarı gösterilecek bir kayıt kimliği dönmemelidir.
        """
        response = APIClient().post('/api/inquiries/', {
            'full_name': 'Deneme Kişi', 'email': 'ziyaretci@example.com', 'service': self.companion.id,
            'message': 'Babam için hastane randevusuna eşlik istiyoruz.', 'consent': False,
        }, format='json')

        self.assertEqual(response.status_code, 400)
        self.assertNotIn('id', response.data)
        self.assertFalse(ServiceInquiry.objects.exists())
