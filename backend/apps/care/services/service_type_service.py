"""Hizmet türleri için iş akışları ve okuma servisleri."""

from django.db import transaction

from apps.care.defaults import DEFAULT_SERVICE_TYPES
from apps.care.models import ServiceType


def list_active_services():
    """
    Başvuru ve hızlı talep formlarında gösterilen aktif hizmetleri döndürür.

    Returns:
        QuerySet[ServiceType]: Gösterim sırasıyla aktif hizmetler.
    """
    return ServiceType.objects.active()


@transaction.atomic
def create_default_service_types():
    """
    Varsayılan hizmet türlerini slug'a göre oluşturur, değişmiş olanları günceller.

    Değeri aynı olan mevcut kayıtlara dokunulmaz; bu nedenle tekrar çalıştırılabilir.

    Returns:
        dict[str, int]: `created` ve `updated` kayıt sayıları.
    """
    created = 0
    updated = 0
    for data in DEFAULT_SERVICE_TYPES:
        fields = {key: value for key, value in data.items() if key != 'slug'}
        service, was_created = ServiceType.objects.get_or_create(slug=data['slug'], defaults=fields)
        if was_created:
            created += 1
            continue
        changed = [key for key, value in fields.items() if getattr(service, key) != value]
        if changed:
            for key in changed:
                setattr(service, key, fields[key])
            service.save(update_fields=changed)
            updated += 1
    return {'created': created, 'updated': updated}
