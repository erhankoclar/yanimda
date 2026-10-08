"""care testlerinde ortak kullanılan veri oluşturma yardımcıları; kayıtları factory-boy fabrikaları üretir."""

from datetime import timedelta

from django.utils import timezone

from apps.accounts.factories import UserFactory
from apps.care.factories import CareRequestFactory, ServiceTypeFactory
from apps.care.models import CareRequest
from apps.geo.factories import NeighborhoodFactory


def make_user(**overrides):
    """
    Benzersiz e-postalı standart kullanıcı oluşturur.

    Args:
        **overrides (Any): UserFactory alanlarını ezen değerler.

    Returns:
        User: Oluşturulan kullanıcı.
    """
    return UserFactory(**overrides)


def make_service(**overrides):
    """
    Benzersiz slug'lı aktif hizmet türü oluşturur.

    Args:
        **overrides (Any): Model alanlarını ezen değerler.

    Returns:
        ServiceType: Oluşturulan hizmet türü.
    """
    return ServiceTypeFactory(**overrides)


def care_request_data(**overrides):
    """
    Geçerli bir talep için model alanlarını (başvuru sahibi ve hizmet hariç) döndürür.

    Args:
        **overrides (Any): Varsayılan alanları ezen değerler.

    Returns:
        dict[str, Any]: Talep alanları; `neighborhood` yeni oluşturulmuş bir Neighborhood nesnesidir
        (API gövdesi için `.pk` kullanılmalıdır).
    """
    return {
        'elder_full_name': 'Fatma Yılmaz',
        'elder_age': 78,
        'relationship': CareRequest.Relationship.PARENT,
        'elder_notes': 'Yürürken desteğe ihtiyaç duyuyor.',
        'preferred_date': timezone.localdate() + timedelta(days=3),
        'time_slot': CareRequest.TimeSlot.MORNING,
        'neighborhood': NeighborhoodFactory(),
        'address': 'Örnek Mah. Deneme Sok. No: 1',
        'contact_phone': '05551112233',
        **overrides,
    }


def make_care_request(applicant=None, service=None, **overrides):
    """
    Veritabanında geçerli bir hizmet talebi oluşturur.

    Args:
        applicant (Optional[User]): Başvuru sahibi; verilmezse yeni kullanıcı oluşturulur.
        service (Optional[ServiceType]): Hizmet; verilmezse yeni hizmet oluşturulur.
        **overrides (Any): Talep alanlarını ezen değerler.

    Returns:
        CareRequest: Oluşturulan talep.
    """
    related = {key: value for key, value in (('applicant', applicant), ('service', service)) if value is not None}
    return CareRequestFactory(**related, **care_request_data(**overrides))
