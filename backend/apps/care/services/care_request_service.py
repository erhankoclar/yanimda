"""Hizmet başvuruları (CareRequest) için iş akışları ve okuma servisleri."""

from django.db import IntegrityError, transaction
from django.utils import timezone
from django.utils.translation import gettext

from apps.care.exceptions import DuplicateOpenRequestError, InvalidStatusTransitionError
from apps.care.models import CareRequest
from apps.care.text import person_name_key


def duplicate_message(elder_full_name):
    """
    Mükerrer başvuru hata mesajını etkin dilde oluşturur.

    Args:
        elder_full_name (str): Yaşlının adı soyadı.

    Returns:
        str: Çevrilmiş hata mesajı.
    """
    return gettext(
        'You already have an open request for this service for %(elder)s. '
        'You can apply again when it is completed or cancelled.'
    ) % {'elder': elder_full_name.strip()}


def has_open_duplicate(applicant, service, elder_full_name):
    """
    Başvuru sahibinin aynı yaşlı için aynı hizmette açık bir başvurusu olup olmadığını söyler.

    Args:
        applicant (User): Başvuru sahibi.
        service (ServiceType): Seçilen hizmet.
        elder_full_name (str): Yaşlının adı soyadı; Türkçe harf ve büyük/küçük harf duyarsız karşılaştırılır.

    Returns:
        bool: Açık mükerrer başvuru varsa True.
    """
    return CareRequest.objects.open().filter(
        applicant=applicant, service=service, elder_name_key=person_name_key(elder_full_name),
    ).exists()


def create_request(applicant, *, consent, **data):
    """
    Başvuru sahibinin onayını kaydederek yeni başvuru oluşturur.

    Eşzamanlı iki istek uygulama kontrolünü birlikte geçerse veritabanındaki
    kısmi benzersizlik kısıtı ikinciyi engeller; bu durum da iş kuralı hatasına çevrilir.

    Args:
        applicant (User): Başvuru sahibi.
        consent (bool): Doğrulanmış kişisel veri onayı.
        **data (Any): Doğrulanmış başvuru alanları (hizmet, yaşlı, zaman, adres, iletişim).

    Returns:
        CareRequest: Oluşturulan başvuru.

    Raises:
        DuplicateOpenRequestError: Aynı yaşlı ve hizmet için açık başvuru varsa.
    """
    if has_open_duplicate(applicant, data['service'], data['elder_full_name']):
        raise DuplicateOpenRequestError('service', duplicate_message(data['elder_full_name']))
    try:
        with transaction.atomic():
            return CareRequest.objects.create(applicant=applicant, consent_given_at=timezone.now(), **data)
    except IntegrityError as error:
        raise DuplicateOpenRequestError('service', duplicate_message(data['elder_full_name'])) from error


def list_for_applicant(applicant):
    """
    Başvuru sahibinin kendi başvurularını hizmetleriyle birlikte döndürür.

    Args:
        applicant (User): Oturumdaki kullanıcı.

    Returns:
        QuerySet[CareRequest]: Kullanıcının başvuruları.
    """
    return CareRequest.objects.filter(applicant=applicant).select_related('service').prefetch_related('service__translations')


def list_for_admin():
    """
    Admin listesi için tüm başvuruları hizmet ve başvuru sahibiyle döndürür.

    Returns:
        QuerySet[CareRequest]: Tüm başvurular.
    """
    return CareRequest.objects.select_related('service', 'applicant').prefetch_related('service__translations')


def next_statuses(care_request):
    """
    Başvurunun mevcut durumundan geçilebilecek durumları döndürür.

    Args:
        care_request (CareRequest): Başvuru.

    Returns:
        list[str]: İzin verilen hedef durumlar; son durumlarda boş liste.
    """
    return list(CareRequest.STATUS_TRANSITIONS[care_request.status])


def can_change_status(care_request, new_status):
    """
    Başvurunun verilen duruma taşınıp taşınamayacağını söyler.

    Aynı durumun tekrar verilmesi her zaman serbesttir; böylece yalnızca not güncellenebilir.

    Args:
        care_request (CareRequest): Başvuru.
        new_status (str): Hedef durum.

    Returns:
        bool: Geçişe izin veriliyorsa True.
    """
    return new_status == care_request.status or new_status in CareRequest.STATUS_TRANSITIONS[care_request.status]


def transition_message(care_request, new_status):
    """
    İzin verilmeyen durum geçişi için hata mesajını oluşturur.

    Args:
        care_request (CareRequest): Başvuru.
        new_status (str): İstenen durum.

    Returns:
        str: Çevrilmiş hata mesajı.
    """
    return gettext('A request in "%(current)s" status cannot be moved to "%(target)s".') % {
        'current': care_request.get_status_display(),
        'target': CareRequest.Status(new_status).label,
    }


def update_by_admin(care_request, *, status=None, admin_note=None):
    """
    Yönetici güncellemesiyle başvurunun durumunu ve/veya yönetici notunu değiştirir.

    Args:
        care_request (CareRequest): Güncellenecek başvuru.
        status (Optional[str]): Yeni durum; verilmezse durum değişmez.
        admin_note (Optional[str]): Yeni yönetici notu; verilmezse not değişmez.

    Returns:
        CareRequest: Güncellenmiş başvuru.

    Raises:
        InvalidStatusTransitionError: Durum geçişine izin verilmiyorsa.
    """
    fields = []
    if status is not None:
        if not can_change_status(care_request, status):
            raise InvalidStatusTransitionError('status', transition_message(care_request, status))
        care_request.status = status
        fields.append('status')
    if admin_note is not None:
        care_request.admin_note = admin_note
        fields.append('admin_note')
    if fields:
        care_request.save(update_fields=[*fields, 'updated_at'])
    return care_request
