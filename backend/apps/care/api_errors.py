"""Servis katmanındaki iş kuralı hatalarını API yanıtına çeviren yardımcılar."""

from rest_framework import serializers


def as_validation_error(error):
    """
    Servisin fırlattığı iş kuralı hatasını alan bazlı DRF doğrulama hatasına çevirir.

    Args:
        error (CareRuleError): Servisten gelen hata.

    Returns:
        serializers.ValidationError: `{alan: [mesaj]}` biçiminde 400 yanıtı üretecek hata.
    """
    return serializers.ValidationError({error.field: [error.message]})
