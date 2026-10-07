from django.contrib.auth import get_user_model
from django.utils.translation import gettext
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from apps.care import api_descriptions
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


class StatusCountSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=CareRequest.Status.choices, help_text=_('Status value.'))
    label = serializers.CharField(help_text=_('Translated label of the status.'))
    count = serializers.IntegerField(help_text=_('Number of requests in this status.'))


class ServiceCountSerializer(serializers.Serializer):
    service_id = serializers.IntegerField(help_text=_('Identifier of the service type.'))
    name = serializers.CharField(help_text=_('Name of the service type.'))
    count = serializers.IntegerField(help_text=_('Number of requests for this service type.'))


class DailyCountSerializer(serializers.Serializer):
    date = serializers.DateField(help_text=_('Day in the server time zone.'))
    count = serializers.IntegerField(help_text=_('Number of requests created on this day.'))


class DashboardStatsSerializer(serializers.Serializer):
    """Admin dashboard istatistiklerinin yanıt şekli."""

    total_requests = serializers.IntegerField(help_text=_('Number of all requests.'))
    open_requests = serializers.IntegerField(help_text=_('Requests that are not completed or cancelled.'))
    requests_last_7_days = serializers.IntegerField(help_text=_('Requests created in the last 7 days.'))
    total_applicants = serializers.IntegerField(help_text=_('Active users without admin rights.'))
    by_status = StatusCountSerializer(many=True, help_text=_('Request count of every status, in flow order.'))
    by_service = ServiceCountSerializer(many=True, help_text=_('Request count of every service type.'))
    daily = DailyCountSerializer(many=True, help_text=_('Requests per day for the last 14 days, oldest first.'))


class DashboardQuerySerializer(serializers.Serializer):
    """Dashboard sorgu parametrelerini doğrular."""

    days = serializers.ChoiceField(
        choices=[7, 30, 90], default=30, help_text=api_descriptions.ADMIN_DASHBOARD_DAYS_HELP_TEXT,
    )
    source = serializers.ChoiceField(
        choices=['all', 'inquiries', 'requests'], default='all',
        help_text=api_descriptions.ADMIN_DASHBOARD_SOURCE_HELP_TEXT,
    )


class ComparisonCardSerializer(serializers.Serializer):
    value = serializers.IntegerField(help_text=_('Value for this month until today.'))
    previous = serializers.IntegerField(help_text=_('Value for the same days of the previous month.'))
    change_percent = serializers.IntegerField(
        allow_null=True, help_text=_('Rounded change in percent; null when the previous value is zero.'),
    )


class OpenRequestsCardSerializer(serializers.Serializer):
    value = serializers.IntegerField(help_text=_('Applications that are new, reviewing or assigned.'))
    new = serializers.IntegerField(help_text=_('Open applications that nobody has reviewed yet.'))


class ServicesCardSerializer(serializers.Serializer):
    value = serializers.IntegerField(help_text=_('Number of active service types.'))
    top_service = serializers.CharField(
        allow_null=True, help_text=_('Service with the most inquiries and applications; null without data.'),
    )


class DashboardCardsSerializer(serializers.Serializer):
    total_demand = ComparisonCardSerializer(help_text=_('Quick inquiries and applications together.'))
    open_requests = OpenRequestsCardSerializer(help_text=_('Applications waiting for the team.'))
    inquiries = ComparisonCardSerializer(help_text=_('Quick inquiries from the landing page.'))
    services = ServicesCardSerializer(help_text=_('Active service types.'))


class SeriesDatasetSerializer(serializers.Serializer):
    service_id = serializers.IntegerField(help_text=_('Identifier of the service type.'))
    name = serializers.CharField(help_text=_('Name of the service type.'))
    icon = serializers.CharField(help_text=_('Icon key of the service type.'))
    counts = serializers.ListField(
        child=serializers.IntegerField(), help_text=_('Count for every label, in the same order.'),
    )


class DashboardSeriesSerializer(serializers.Serializer):
    bucket = serializers.ChoiceField(choices=['day', 'week'], help_text=_('Length of one period.'))
    labels = serializers.ListField(
        child=serializers.DateField(), help_text=_('Start date of every period, oldest first.'),
    )
    datasets = SeriesDatasetSerializer(many=True, help_text=_('One line per active service type.'))


class RecentItemSerializer(serializers.Serializer):
    type = serializers.ChoiceField(choices=['inquiry', 'request'], help_text=_('Quick inquiry or application.'))
    id = serializers.IntegerField(help_text=_('Identifier of the quick inquiry or application.'))
    title = serializers.CharField(help_text=_('Contact name for inquiries, elder name for applications.'))
    service = ServiceTypeSerializer(help_text=_('Requested service type.'))
    created_at = serializers.DateTimeField(help_text=_('Creation time.'))
    status = serializers.CharField(allow_null=True, help_text=_('Application status; null for inquiries.'))


class PendingRequestSerializer(serializers.ModelSerializer):
    service = ServiceTypeSerializer(read_only=True, help_text=_('Requested service type.'))

    class Meta:
        model = CareRequest
        fields = ['id', 'service', 'elder_full_name', 'preferred_date', 'status', 'created_at']
        read_only_fields = fields


class DashboardSerializer(serializers.Serializer):
    """Admin dashboard yanıtının şekli."""

    cards = DashboardCardsSerializer(help_text=_('Summary cards.'))
    series = DashboardSeriesSerializer(help_text=_('Service chart data.'))
    recent = RecentItemSerializer(many=True, help_text=_('Latest quick inquiries and applications.'))
    pending = PendingRequestSerializer(many=True, help_text=_('Oldest applications waiting for review.'))
    status_breakdown = StatusCountSerializer(many=True, help_text=_('Application count of every status.'))
