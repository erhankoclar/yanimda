from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from apps.care.models import CareRequest
from apps.care.serializers import ServiceTypeSerializer


class ApplicantSummarySerializer(serializers.ModelSerializer):
    """Admin ekranlarında talebin başvuru sahibini özetler."""

    full_name = serializers.CharField(
        source='get_full_name', read_only=True, help_text=_('First and last name of the applicant.'),
    )

    class Meta:
        model = get_user_model()
        fields = ['id', 'email', 'full_name', 'phone']
        extra_kwargs = {
            'email': {'help_text': _('Login email of the applicant.')},
            'phone': {'help_text': _('Profile phone of the applicant; may differ from the request contact phone.')},
        }


class AdminCareRequestListSerializer(serializers.ModelSerializer):
    """Admin talep tablosunun bir satırı."""

    applicant = ApplicantSummarySerializer(read_only=True, help_text=_('Applicant who created the request.'))
    service = ServiceTypeSerializer(read_only=True, help_text=_('Requested service type.'))
    status_display = serializers.CharField(
        source='get_status_display', read_only=True, help_text=_('Translated label of the status.'),
    )
    time_slot_display = serializers.CharField(
        source='get_time_slot_display', read_only=True, help_text=_('Translated label of the time slot.'),
    )

    class Meta:
        model = CareRequest
        fields = [
            'id', 'applicant', 'service', 'elder_full_name', 'elder_age', 'city', 'district',
            'preferred_date', 'time_slot', 'time_slot_display', 'contact_phone',
            'status', 'status_display', 'created_at',
        ]
        read_only_fields = fields
