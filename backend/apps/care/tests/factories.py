"""care testlerinde ortak kullanılan veri oluşturma yardımcıları."""

from datetime import timedelta
from itertools import count

from django.contrib.auth import get_user_model
from django.utils import timezone

from apps.care.models import CareRequest, ServiceType

_sequence = count(1)


def make_user(**overrides):
    """
    Benzersiz e-postalı standart kullanıcı oluşturur.

    Args:
        **overrides (Any): create_user'a aktarılacak alanlar.

    Returns:
        User: Oluşturulan kullanıcı.
    """
    number = next(_sequence)
    data = {'email': f'kullanici{number}@example.com', 'password': 'Yanimda-Guclu-2026', **overrides}
    return get_user_model().objects.create_user(**data)


def make_service(**overrides):
    """
    Benzersiz slug'lı aktif hizmet türü oluşturur.

    Args:
        **overrides (Any): Model alanlarını ezen değerler.

    Returns:
        ServiceType: Oluşturulan hizmet türü.
    """
    number = next(_sequence)
    data = {
        'name': f'Hizmet {number}', 'slug': f'hizmet-{number}', 'description': 'Açıklama',
        'icon': 'companion', 'sort_order': number, **overrides,
    }
    return ServiceType.objects.create(**data)


def care_request_data(**overrides):
    """
    Geçerli bir talep için model alanlarını (başvuru sahibi ve hizmet hariç) döndürür.

    Args:
        **overrides (Any): Varsayılan alanları ezen değerler.

    Returns:
        dict[str, Any]: Talep alanları.
    """
    return {
        'elder_full_name': 'Fatma Yılmaz',
        'elder_age': 78,
        'relationship': CareRequest.Relationship.PARENT,
        'elder_notes': 'Yürürken desteğe ihtiyaç duyuyor.',
        'preferred_date': timezone.localdate() + timedelta(days=3),
        'time_slot': CareRequest.TimeSlot.MORNING,
        'city': 'Samsun',
        'district': 'İlkadım',
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
    data = care_request_data(**overrides)
    data.setdefault('consent_given_at', timezone.now())
    return CareRequest.objects.create(
        applicant=applicant or make_user(), service=service or make_service(), **data,
    )
