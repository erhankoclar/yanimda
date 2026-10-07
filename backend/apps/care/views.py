from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema, extend_schema_view
from rest_framework import generics, permissions

from apps.care import api_descriptions
from apps.care.api_errors import as_validation_error
from apps.care.exceptions import CareRuleError
from apps.care.serializers import CareRequestSerializer, ServiceTypeSerializer
from apps.care.services import care_request_service, service_type_service
from apps.care.throttles import CareRequestCreateRateThrottle


@extend_schema(
    tags=['services'],
    summary=api_descriptions.SERVICE_LIST_SUMMARY,
    description=api_descriptions.SERVICE_LIST_VIEW_DESCRIPTION,
)
class ServiceTypeListView(generics.ListAPIView):
    __doc__ = api_descriptions.SERVICE_LIST_VIEW_DESCRIPTION

    serializer_class = ServiceTypeSerializer
    permission_classes = [permissions.AllowAny]
    pagination_class = None

    def get_queryset(self):
        """
        Aktif hizmetleri servis üzerinden döndürür.

        Returns:
            QuerySet[ServiceType]: Aktif hizmetler.
        """
        return service_type_service.list_active_services()


class ApplicantRequestQuerysetMixin:
    """Talepleri isteği yapan başvuru sahibiyle sınırlar."""

    def get_queryset(self):
        """
        Yalnızca oturumdaki kullanıcının taleplerini döndürür.

        Returns:
            QuerySet[CareRequest]: Hizmetiyle birlikte yüklenmiş kullanıcı talepleri.
        """
        return care_request_service.list_for_applicant(self.request.user)


@extend_schema_view(
    get=extend_schema(
        tags=['requests'],
        summary=api_descriptions.CARE_REQUEST_LIST_SUMMARY,
        description=api_descriptions.CARE_REQUEST_LIST_VIEW_DESCRIPTION,
    ),
    post=extend_schema(
        tags=['requests'],
        summary=api_descriptions.CARE_REQUEST_CREATE_SUMMARY,
        description=api_descriptions.CARE_REQUEST_CREATE_VIEW_DESCRIPTION,
    ),
)
class CareRequestListCreateView(ApplicantRequestQuerysetMixin, generics.ListCreateAPIView):
    __doc__ = api_descriptions.CARE_REQUEST_LIST_VIEW_DESCRIPTION

    serializer_class = CareRequestSerializer
    throttle_classes = [CareRequestCreateRateThrottle]

    def perform_create(self, serializer):
        """
        Doğrulanmış başvuruyu servis üzerinden oturumdaki kullanıcı adına kaydeder.

        Args:
            serializer (CareRequestSerializer): Doğrulanmış serializer; yanıt için oluşturulan başvuru atanır.

        Raises:
            ValidationError: Servis bir iş kuralı ihlali bildirirse (ör. eşzamanlı mükerrer başvuru).
        """
        try:
            serializer.instance = care_request_service.create_request(self.request.user, **serializer.validated_data)
        except CareRuleError as error:
            raise as_validation_error(error) from error


@extend_schema(
    tags=['requests'],
    summary=api_descriptions.CARE_REQUEST_DETAIL_SUMMARY,
    description=api_descriptions.CARE_REQUEST_DETAIL_VIEW_DESCRIPTION,
    parameters=[
        OpenApiParameter(
            'id', OpenApiTypes.INT, OpenApiParameter.PATH,
            description=api_descriptions.CARE_REQUEST_ID_PARAMETER_DESCRIPTION,
        ),
    ],
)
class CareRequestDetailView(ApplicantRequestQuerysetMixin, generics.RetrieveAPIView):
    __doc__ = api_descriptions.CARE_REQUEST_DETAIL_VIEW_DESCRIPTION

    serializer_class = CareRequestSerializer
