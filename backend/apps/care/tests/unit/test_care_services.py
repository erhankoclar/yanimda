from django.test import TestCase

from apps.care.exceptions import DuplicateOpenRequestError, InvalidStatusTransitionError
from apps.care.models import CareRequest, ServiceInquiry
from apps.care.services import care_request_service, inquiry_service, service_type_service
from apps.care.tests.factories import care_request_data, make_care_request, make_service, make_user
from apps.geo.factories import NeighborhoodFactory


class CareRequestServiceTests(TestCase):
    def test_create_request_records_consent_and_starts_new(self):
        """
        Başvuru oluşturma servisinin onay zamanını kaydedip başvuruyu yeni durumunda açtığını doğrular.

        Senaryo:
        - Servis geçerli verilerle çağrılır.

        Beklenti:
        - Başvuru kullanıcıya bağlı, `new` durumunda ve onay zamanı dolu olmalıdır.
        """
        applicant = make_user()

        created = care_request_service.create_request(
            applicant, consent=True, service=make_service(), **care_request_data(),
        )

        self.assertEqual(created.applicant, applicant)
        self.assertEqual(created.status, CareRequest.Status.NEW)
        self.assertIsNotNone(created.consent_given_at)

    def test_create_request_rejects_open_duplicate(self):
        """Aynı yaşlı ve hizmet için açık başvuru varken servisin iş kuralı hatası fırlattığını doğrular."""
        existing = make_care_request()

        with self.assertRaises(DuplicateOpenRequestError) as context:
            care_request_service.create_request(
                existing.applicant, consent=True, service=existing.service,
                **care_request_data(elder_full_name='FATMA YILMAZ'),
            )

        self.assertEqual(context.exception.field, 'service')

    def test_update_by_admin_moves_status_and_note(self):
        """
        Yönetici güncellemesinin izinli durum geçişini ve notu kaydettiğini doğrular.

        Senaryo:
        - Yeni başvuru inceleniyor durumuna notla taşınır.

        Beklenti:
        - Durum ve not veritabanına yazılmalıdır.
        """
        care_request = make_care_request()

        care_request_service.update_by_admin(care_request, status='reviewing', admin_note='Arandı')

        care_request.refresh_from_db()
        self.assertEqual((care_request.status, care_request.admin_note), ('reviewing', 'Arandı'))

    def test_update_by_admin_rejects_invalid_transition(self):
        """İzin verilmeyen durum geçişinde servisin hata fırlattığını ve kaydı değiştirmediğini doğrular."""
        care_request = make_care_request()

        with self.assertRaises(InvalidStatusTransitionError):
            care_request_service.update_by_admin(care_request, status='completed')

        care_request.refresh_from_db()
        self.assertEqual(care_request.status, CareRequest.Status.NEW)

    def test_list_for_applicant_returns_only_own_requests(self):
        """Başvuru sahibi listesinin yalnızca kendi başvurularını içerdiğini doğrular."""
        own = make_care_request()
        make_care_request()

        self.assertEqual(list(care_request_service.list_for_applicant(own.applicant)), [own])


class InquiryAndServiceTypeServiceTests(TestCase):
    def test_create_inquiry_stores_consent_time_and_drops_honeypot(self):
        """
        Hızlı talep servisinin onay zamanını kaydedip mahallesiyle kaydettiğini ve tuzak alanını saklamadığını doğrular.

        Senaryo:
        - Servis geçerli verilerle ve bir mahalle nesnesiyle çağrılır.

        Beklenti:
        - Talep onay zamanı ve mahalle bilgisiyle kaydedilmelidir.
        """
        neighborhood = NeighborhoodFactory()
        inquiry = inquiry_service.create_inquiry(
            full_name='Deneme', email='d@example.com', service=make_service(), message='Kurgusal açıklama',
            consent=True, website='', neighborhood=neighborhood,
        )

        self.assertTrue(ServiceInquiry.objects.filter(pk=inquiry.pk, consent_given_at__isnull=False).exists())
        self.assertEqual(inquiry.neighborhood, neighborhood)

    def test_list_active_services_hides_inactive_in_order(self):
        """Aktif hizmet listesinin pasifleri gizleyip sıra numarasına göre döndüğünü doğrular."""
        second = make_service(sort_order=20)
        first = make_service(sort_order=10)
        make_service(is_active=False)

        self.assertEqual(list(service_type_service.list_active_services()), [first, second])
