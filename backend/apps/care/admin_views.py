from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema
from rest_framework import filters, generics, permissions

from apps.care import api_descriptions
from apps.care.admin_serializers import AdminCareRequestListSerializer
from apps.care.filters import AdminCareRequestFilter
from apps.care.models import CareRequest


class AdminCareRequestQuerysetMixin:
    """Admin talep endpoint'lerinin ortak yetki ve sorgu ayarları."""

    permission_classes = [permissions.IsAdminUser]

    def get_queryset(self):
        """
        Tüm talepleri hizmet ve başvuru sahibiyle birlikte döndürür.

        Returns:
            QuerySet[CareRequest]: İlişkileri önceden yüklenmiş talepler.
        """
        return CareRequest.objects.select_related('service', 'applicant')


@extend_schema(
    tags=['admin'],
    summary=api_descriptions.ADMIN_REQUEST_LIST_SUMMARY,
    description=api_descriptions.ADMIN_REQUEST_LIST_VIEW_DESCRIPTION,
)
class AdminCareRequestListView(AdminCareRequestQuerysetMixin, generics.ListAPIView):
    __doc__ = api_descriptions.ADMIN_REQUEST_LIST_VIEW_DESCRIPTION

    serializer_class = AdminCareRequestListSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = AdminCareRequestFilter
    search_fields = [
        'elder_full_name', 'applicant__email', 'city', 'district', 'contact_phone',
    ]
    ordering_fields = ['created_at', 'preferred_date', 'status']
    ordering = ['-created_at']
