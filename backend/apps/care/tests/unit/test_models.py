from datetime import timedelta

from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.db.models import ProtectedError
from django.test import TestCase
from django.utils import timezone

from apps.care.models import CareRequest, ServiceType
from apps.care.services import care_request_service
from apps.care.tests.factories import make_care_request, make_service, make_user


class ServiceTypeModelTests(TestCase):
    def test_default_ordering_uses_sort_order(self):
        """
        Hizmet türlerinin sıra numarasına göre listelendiğini doğrular.

        Senaryo:
        - Sıra numarası ters olan iki hizmet oluşturulur.

        Beklenti:
        - Küçük sıra numaralı hizmet önce gelmelidir.
        """
        ServiceType.objects.create(name='B', slug='b', description='-', icon='x', sort_order=20)
        ServiceType.objects.create(name='A', slug='a', description='-', icon='x', sort_order=10)

        self.assertEqual(list(ServiceType.objects.values_list('slug', flat=True)), ['a', 'b'])

    def test_slug_is_unique(self):
        """Aynı slug ile ikinci hizmet türü oluşturulamadığını doğrular (hata yolu)."""
        ServiceType.objects.create(name='A', slug='a', description='-', icon='x')

        with self.assertRaises(IntegrityError):
            ServiceType.objects.create(name='A2', slug='a', description='-', icon='x')

    def test_str_returns_name(self):
        """Metin temsilinin hizmet adı olduğunu doğrular."""
        service = ServiceType(name='Refakat', slug='refakat', description='-', icon='companion')

        self.assertEqual(str(service), 'Refakat')


class CareRequestModelTests(TestCase):
    def test_new_request_starts_with_new_status(self):
        """Yeni oluşturulan talebin varsayılan durumunun `new` olduğunu doğrular."""
        care_request = make_care_request()

        self.assertEqual(care_request.status, CareRequest.Status.NEW)
        self.assertEqual(care_request.admin_note, '')

    def test_requests_are_ordered_newest_first(self):
        """
        Taleplerin en yeniden eskiye sıralandığını doğrular.

        Senaryo:
        - İki talep oluşturulur, ilkinin oluşturulma zamanı geriye alınır.

        Beklenti:
        - Varsayılan sıralamada ikinci talep önce gelmelidir.
        """
        older = make_care_request()
        newer = make_care_request()
        CareRequest.objects.filter(pk=older.pk).update(created_at=timezone.now() - timedelta(days=1))

        self.assertEqual(list(CareRequest.objects.all()), [newer, older])

    def test_service_with_requests_cannot_be_deleted(self):
        """
        Talebi olan hizmet türünün silinemediğini doğrular (veri bütünlüğü).

        Senaryo:
        - Bir hizmete bağlı talep oluşturulur ve hizmet silinmeye çalışılır.

        Beklenti:
        - ProtectedError fırlatılmalı ve talep korunmalıdır.
        """
        service = make_service()
        make_care_request(service=service)

        with self.assertRaises(ProtectedError):
            service.delete()
        self.assertEqual(CareRequest.objects.count(), 1)

    def test_deleting_applicant_removes_requests(self):
        """Başvuru sahibi silindiğinde taleplerinin de silindiğini doğrular (kişisel veri temizliği)."""
        applicant = make_user()
        make_care_request(applicant=applicant)

        applicant.delete()

        self.assertFalse(CareRequest.objects.exists())

    def test_elder_age_limits_are_validated(self):
        """
        Yaşlı yaşının 40-120 aralığı dışında reddedildiğini doğrular (hata yolu).

        Senaryo:
        - Yaşı 30 ve 130 olan talepler tam doğrulamadan geçirilir.

        Beklenti:
        - Her ikisi de `elder_age` alanında ValidationError vermelidir.
        """
        for age in (30, 130):
            care_request = make_care_request()
            care_request.elder_age = age
            with self.assertRaises(ValidationError) as context:
                care_request.full_clean()
            self.assertIn('elder_age', context.exception.error_dict)

    def test_str_contains_id_service_and_elder(self):
        """Metin temsilinin talep numarası, hizmet ve yaşlı adını içerdiğini doğrular."""
        care_request = make_care_request(service=make_service(name='Refakat'))

        self.assertEqual(str(care_request), f'#{care_request.pk} Refakat - Fatma Yılmaz')


class CareRequestStatusTransitionTests(TestCase):
    def test_allowed_forward_flow(self):
        """
        Durumun ileri akışta yalnızca bir sonraki adıma veya iptale geçebildiğini doğrular.

        Senaryo:
        - Her açık durum için izin verilen hedefler kontrol edilir.

        Beklenti:
        - new→reviewing, reviewing→assigned, assigned→completed ve her açık durumdan cancelled izinli olmalıdır.
        """
        Status = CareRequest.Status
        expected = {
            Status.NEW: {Status.REVIEWING, Status.CANCELLED},
            Status.REVIEWING: {Status.ASSIGNED, Status.CANCELLED},
            Status.ASSIGNED: {Status.COMPLETED, Status.CANCELLED},
        }
        for current, targets in expected.items():
            with self.subTest(current=current):
                care_request = CareRequest(status=current)
                self.assertEqual(set(care_request_service.next_statuses(care_request)), targets)
                for target in targets:
                    self.assertTrue(care_request_service.can_change_status(care_request, target))

    def test_skipping_or_going_back_is_not_allowed(self):
        """
        Adım atlamanın ve geri dönmenin engellendiğini doğrular (hata yolu).

        Senaryo:
        - new→completed atlaması ve assigned→new geri dönüşü denenir.

        Beklenti:
        - Her iki geçiş de reddedilmelidir.
        """
        self.assertFalse(care_request_service.can_change_status(CareRequest(status=CareRequest.Status.NEW), CareRequest.Status.COMPLETED))
        self.assertFalse(care_request_service.can_change_status(CareRequest(status=CareRequest.Status.ASSIGNED), CareRequest.Status.NEW))

    def test_final_statuses_cannot_change(self):
        """Tamamlanan ve iptal edilen taleplerin başka duruma geçemediğini doğrular."""
        for final in (CareRequest.Status.COMPLETED, CareRequest.Status.CANCELLED):
            with self.subTest(final=final):
                care_request = CareRequest(status=final)
                self.assertEqual(care_request_service.next_statuses(care_request), [])
                self.assertFalse(care_request_service.can_change_status(care_request, CareRequest.Status.NEW))

    def test_same_status_is_always_allowed(self):
        """Mevcut durumun tekrar gönderilmesinin (yalnızca not güncelleme) her durumda serbest olduğunu doğrular."""
        for current in CareRequest.Status.values:
            with self.subTest(current=current):
                self.assertTrue(care_request_service.can_change_status(CareRequest(status=current), current))


class CareRequestOpenConstraintTests(TestCase):
    def test_constraint_blocks_second_open_request(self):
        """
        Veritabanı kısıtının aynı yaşlı ve hizmet için ikinci açık talebi engellediğini doğrular.

        Senaryo:
        - Aynı başvuru sahibi, hizmet ve büyük/küçük harfi farklı yaşlı adıyla iki talep doğrudan kaydedilir.

        Beklenti:
        - İkinci kayıt IntegrityError vermelidir.
        """
        first = make_care_request()

        with self.assertRaises(IntegrityError):
            make_care_request(applicant=first.applicant, service=first.service, elder_full_name='FATMA YILMAZ')

    def test_constraint_ignores_closed_requests(self):
        """Kapanmış (tamamlanan/iptal) talebin yeni açık talebi engellemediğini doğrular."""
        first = make_care_request(status=CareRequest.Status.COMPLETED)

        second = make_care_request(applicant=first.applicant, service=first.service)

        self.assertEqual(second.status, CareRequest.Status.NEW)


class ServiceInquiryModelTests(TestCase):
    def test_str_contains_id_name_and_service(self):
        """Hızlı talebin metin temsilinin numara, ad ve hizmeti içerdiğini doğrular."""
        from apps.care.models import ServiceInquiry

        inquiry = ServiceInquiry.objects.create(
            full_name='Deneme Kişi', email='d@example.com', service=make_service(name='Refakat'),
            message='Açıklama', consent_given_at=timezone.now(),
        )

        self.assertEqual(str(inquiry), f'#{inquiry.pk} Deneme Kişi - Refakat')

    def test_service_with_inquiries_cannot_be_deleted(self):
        """Talebi olan hizmetin silinemediğini doğrular (veri bütünlüğü)."""
        from apps.care.models import ServiceInquiry

        service = make_service()
        ServiceInquiry.objects.create(
            full_name='Deneme', email='d@example.com', service=service, message='Açıklama',
            consent_given_at=timezone.now(),
        )

        with self.assertRaises(ProtectedError):
            service.delete()
