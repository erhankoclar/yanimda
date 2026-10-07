from django.contrib.auth import get_user_model
from django.utils.translation import gettext
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


class AdminCareRequestDetailSerializer(AdminCareRequestListSerializer):
    """Admin talep detayı; yalnızca durum ve yönetici notu değiştirilebilir."""

    status = serializers.ChoiceField(
        choices=CareRequest.Status.choices, required=False,
        help_text=_('New status. Must be one of <code>next_statuses</code> or the current status.'),
    )
    admin_note = serializers.CharField(
        required=False, allow_blank=True, max_length=2000,
        help_text=_('Internal note for the admin team. Never shown to the applicant. At most 2000 characters.'),
    )
    relationship_display = serializers.CharField(
        source='get_relationship_display', read_only=True, help_text=_('Translated label of the relationship.'),
    )
    next_statuses = serializers.ListField(
        child=serializers.CharField(), read_only=True,
        help_text=_('Statuses the request can move to from its current status. Empty for final statuses.'),
    )

    class Meta(AdminCareRequestListSerializer.Meta):
        fields = AdminCareRequestListSerializer.Meta.fields + [
            'relationship', 'relationship_display', 'elder_notes', 'address',
            'alternate_contact_name', 'alternate_contact_phone', 'consent_given_at',
            'admin_note', 'next_statuses', 'updated_at',
        ]
        read_only_fields = [field for field in fields if field not in ('status', 'admin_note')]

    def validate_status(self, value):
        """
        Durum değişikliğinin izin verilen geçişlerden biri olduğunu doğrular.

        Args:
            value (str): İstenen yeni durum.

        Returns:
            str: Değiştirilmemiş durum değeri.

        Raises:
            serializers.ValidationError: Geçişe izin verilmiyorsa.
        """
        if not self.instance.can_change_status_to(value):
            raise serializers.ValidationError(
                gettext('A request in "%(current)s" status cannot be moved to "%(target)s".') % {
                    'current': self.instance.get_status_display(),
                    'target': CareRequest.Status(value).label,
                },
            )
        return value
