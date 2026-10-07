import django_filters

from apps.care import api_descriptions
from apps.care.models import CareRequest


class AdminCareRequestFilter(django_filters.FilterSet):
    """Admin talep listesinin filtreleri."""

    status = django_filters.ChoiceFilter(
        choices=CareRequest.Status.choices, help_text=api_descriptions.ADMIN_FILTER_STATUS_HELP_TEXT,
    )
    service = django_filters.NumberFilter(
        field_name='service_id', help_text=api_descriptions.ADMIN_FILTER_SERVICE_HELP_TEXT,
    )
    applicant = django_filters.NumberFilter(
        field_name='applicant_id', help_text=api_descriptions.ADMIN_FILTER_APPLICANT_HELP_TEXT,
    )
    created_from = django_filters.DateFilter(
        field_name='created_at', lookup_expr='date__gte',
        help_text=api_descriptions.ADMIN_FILTER_CREATED_FROM_HELP_TEXT,
    )
    created_to = django_filters.DateFilter(
        field_name='created_at', lookup_expr='date__lte',
        help_text=api_descriptions.ADMIN_FILTER_CREATED_TO_HELP_TEXT,
    )

    class Meta:
        model = CareRequest
        fields = ['status', 'service', 'applicant', 'created_from', 'created_to']
