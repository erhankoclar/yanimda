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


def localized(service, field):
    """
    Hizmetin adını veya açıklamasını etkin dilde döndürür.

    Çeviri django-parler'dan okunur; etkin dilde satır yoksa ayarlardaki yedek dile (Türkçe),
    o da yoksa mevcut herhangi bir dile düşülür.

    Args:
        service (ServiceType): Hizmet türü.
        field (str): `name` veya `description`.

    Returns:
        str: Etkin dildeki metin; hiç çeviri yoksa boş metin.
    """
    return service.safe_translation_getter(field, default='', any_language=True)


def _sync_translations(service, translations):
    """
    Hizmetin dil satırlarını verilen metinlerle eşitler; aynı olan satırlara dokunmaz.

    Args:
        service (ServiceType): Kaydedilmiş hizmet türü.
        translations (dict[str, dict[str, str]]): Dil kodundan `name`/`description` metinlerine eşleme.

    Returns:
        bool: En az bir dil satırı oluşturulduysa veya değiştiyse True.
    """
    existing = {translation.language_code: translation for translation in service.translations.all()}
    changed = False
    for language, texts in translations.items():
        current = existing.get(language)
        if current and all(getattr(current, key) == value for key, value in texts.items()):
            continue
        service.set_current_language(language)
        for key, value in texts.items():
            setattr(service, key, value)
        service.save_translations()
        changed = True
    return changed


@transaction.atomic
def create_default_service_types():
    """
    Varsayılan hizmet türlerini slug'a göre oluşturur, değişmiş olanları ve dil satırlarını günceller.

    Değeri aynı olan mevcut kayıtlara ve çevirilere dokunulmaz; bu nedenle tekrar çalıştırılabilir.

    Returns:
        dict[str, int]: `created` ve `updated` kayıt sayıları.
    """
    created = 0
    updated = 0
    for data in DEFAULT_SERVICE_TYPES:
        fields = {key: value for key, value in data.items() if key not in ('slug', 'translations')}
        service, was_created = ServiceType.objects.get_or_create(slug=data['slug'], defaults=fields)
        changed = [key for key, value in fields.items() if getattr(service, key) != value]
        if changed:
            for key in changed:
                setattr(service, key, fields[key])
            service.save(update_fields=changed)
        translations_changed = _sync_translations(service, data['translations'])
        if was_created:
            created += 1
        elif changed or translations_changed:
            updated += 1
    return {'created': created, 'updated': updated}
