"""Hesapsız hızlı talepler (ServiceInquiry) için iş akışları ve okuma servisleri."""

from django.utils import timezone

from apps.care.models import ServiceInquiry


def create_inquiry(*, full_name, email, service, neighborhood, message, consent, website=''):
    """
    Hızlı talebi onay zamanıyla birlikte kalıcı olarak kaydeder.

    Args:
        full_name (str): Doğrulanmış ve boşlukları temizlenmiş ad soyad.
        email (str): Doğrulanmış, küçük harfli e-posta.
        service (ServiceType): Talep edilen aktif hizmet.
        neighborhood (Neighborhood): Kişinin İstanbul'daki mahallesi.
        message (str): Doğrulanmış açıklama.
        consent (bool): Doğrulanmış onay (True).
        website (str): Boş kalması doğrulanmış spam tuzağı alanı; kaydedilmez.

    Returns:
        ServiceInquiry: Kaydedilen talep.
    """
    return ServiceInquiry.objects.create(
        full_name=full_name, email=email, service=service, neighborhood=neighborhood, message=message,
        consent_given_at=timezone.now(),
    )


def list_for_admin():
    """
    Admin listesi için hızlı talepleri hizmetleriyle en yeniden eskiye döndürür.

    Returns:
        QuerySet[ServiceInquiry]: Tüm hızlı talepler.
    """
    return ServiceInquiry.objects.latest_first()
