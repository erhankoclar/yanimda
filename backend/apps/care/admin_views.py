from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema, extend_schema_view
from rest_framework import filters, generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.care import api_descriptions
from apps.care.admin_serializers import (
    AdminCareRequestDetailSerializer,
    AdminCareRequestListSerializer,
    DashboardQuerySerializer,
    DashboardSerializer,
    DashboardStatsSerializer,
)
from apps.care.services.dashboard_service import build_dashboard
from apps.care.api_errors import as_validation_error
from apps.care.exceptions import CareRuleError
from apps.care.filters import AdminCareRequestFilter
from apps.care.services import care_request_service
from apps.care.services.stats_service import build_dashboard_stats

_ADMIN_REQUEST_ID_PARAMETER = OpenApiParameter(
    'id', OpenApiTypes.INT, OpenApiParameter.PATH,
    description=api_descriptions.ADMIN_REQUEST_ID_PARAMETER_DESCRIPTION,
)


class AdminCareRequestQuerysetMixin:
    """Admin talep endpoint'lerinin ortak yetki ve sorgu ayarları."""

    permission_classes = [permissions.IsAdminUser]

    def get_queryset(self):
        """
        Tüm talepleri hizmet ve başvuru sahibiyle birlikte döndürür.

        Returns:
            QuerySet[CareRequest]: İlişkileri önceden yüklenmiş talepler.
        """
        return care_request_service.list_for_admin()


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


@extend_schema_view(
    get=extend_schema(
        tags=['admin'],
        summary=api_descriptions.ADMIN_REQUEST_DETAIL_SUMMARY,
        description=api_descriptions.ADMIN_REQUEST_DETAIL_VIEW_DESCRIPTION,
        parameters=[_ADMIN_REQUEST_ID_PARAMETER],
    ),
    patch=extend_schema(
        tags=['admin'],
        summary=api_descriptions.ADMIN_REQUEST_UPDATE_SUMMARY,
        description=api_descriptions.ADMIN_REQUEST_UPDATE_VIEW_DESCRIPTION,
        parameters=[_ADMIN_REQUEST_ID_PARAMETER],
    ),
)
class AdminCareRequestDetailView(AdminCareRequestQuerysetMixin, generics.RetrieveUpdateAPIView):
    __doc__ = api_descriptions.ADMIN_REQUEST_DETAIL_VIEW_DESCRIPTION

    serializer_class = AdminCareRequestDetailSerializer
    http_method_names = ['get', 'patch', 'head', 'options']

    def perform_update(self, serializer):
        """
        Doğrulanmış durum ve not değişikliğini servis üzerinden kaydeder.

        Args:
            serializer (AdminCareRequestDetailSerializer): Doğrulanmış serializer.

        Raises:
            ValidationError: Servis durum geçişini reddederse.
        """
        try:
            serializer.instance = care_request_service.update_by_admin(serializer.instance, **serializer.validated_data)
        except CareRuleError as error:
            raise as_validation_error(error) from error


@extend_schema(
    tags=['admin'],
    summary=api_descriptions.ADMIN_STATS_SUMMARY,
    description=api_descriptions.ADMIN_STATS_VIEW_DESCRIPTION,
    responses=DashboardStatsSerializer,
)
class AdminDashboardStatsView(APIView):
    __doc__ = api_descriptions.ADMIN_STATS_VIEW_DESCRIPTION

    permission_classes = [permissions.IsAdminUser]

    def get(self, request):
        """
        Dashboard istatistiklerini hesaplayıp döndürür.

        Args:
            request (Request): Admin kullanıcının isteği.

        Returns:
            Response: DashboardStatsSerializer şeklinde istatistikler.
        """
        return Response(DashboardStatsSerializer(build_dashboard_stats()).data)


@extend_schema(
    tags=['admin'],
    summary=api_descriptions.ADMIN_DASHBOARD_SUMMARY,
    description=api_descriptions.ADMIN_DASHBOARD_VIEW_DESCRIPTION,
    parameters=[DashboardQuerySerializer],
    responses=DashboardSerializer,
)
class AdminDashboardView(APIView):
    __doc__ = api_descriptions.ADMIN_DASHBOARD_VIEW_DESCRIPTION

    permission_classes = [permissions.IsAdminUser]

    def get(self, request):
        """
        Sorgu parametrelerini doğrular ve dashboard verilerini döndürür.

        Args:
            request (Request): Admin kullanıcının isteği; `days` ve `source` parametreleri olabilir.

        Returns:
            Response: DashboardSerializer şeklinde dashboard verileri.

        Raises:
            ValidationError: `days` veya `source` izin verilen değerlerden biri değilse (400).
        """
        query = DashboardQuerySerializer(data=request.query_params)
        query.is_valid(raise_exception=True)
        data = build_dashboard(days=int(query.validated_data['days']), source=query.validated_data['source'])
        return Response(DashboardSerializer(data).data)
