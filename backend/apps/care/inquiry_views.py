from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema
from rest_framework import filters, generics, permissions

from apps.care import api_descriptions
from apps.care.inquiry_serializers import AdminServiceInquirySerializer, ServiceInquirySerializer
from apps.care.models import ServiceInquiry
from apps.care.throttles import InquiryCreateRateThrottle


@extend_schema(
    tags=['inquiries'],
    summary=api_descriptions.INQUIRY_CREATE_SUMMARY,
    description=api_descriptions.INQUIRY_CREATE_VIEW_DESCRIPTION,
)
class ServiceInquiryCreateView(generics.CreateAPIView):
    __doc__ = api_descriptions.INQUIRY_CREATE_VIEW_DESCRIPTION

    serializer_class = ServiceInquirySerializer
    permission_classes = [permissions.AllowAny]
    # Herkese açık formdur; tarayıcıda kalmış eski bir token isteği reddettirmesin.
    authentication_classes = []
    throttle_classes = [InquiryCreateRateThrottle]


@extend_schema(
    tags=['admin'],
    summary=api_descriptions.ADMIN_INQUIRY_LIST_SUMMARY,
    description=api_descriptions.ADMIN_INQUIRY_LIST_VIEW_DESCRIPTION,
)
class AdminServiceInquiryListView(generics.ListAPIView):
    __doc__ = api_descriptions.ADMIN_INQUIRY_LIST_VIEW_DESCRIPTION

    serializer_class = AdminServiceInquirySerializer
    permission_classes = [permissions.IsAdminUser]
    queryset = ServiceInquiry.objects.select_related('service')
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['service']
    search_fields = ['full_name', 'email', 'message']
