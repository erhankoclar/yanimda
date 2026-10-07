from django.contrib.auth import get_user_model
from django.db.models import Count
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import filters, generics, permissions

from apps.accounts import api_descriptions
from apps.accounts.admin_serializers import AdminUserSerializer


class AdminUserQuerysetMixin:
    """Admin kullanıcı endpoint'lerinin ortak yetki ve sorgu ayarları."""

    permission_classes = [permissions.IsAdminUser]
    serializer_class = AdminUserSerializer

    def get_queryset(self):
        """
        Tüm kullanıcıları talep sayılarıyla birlikte döndürür.

        Returns:
            QuerySet[User]: `request_count` ile işaretlenmiş kullanıcılar.
        """
        return get_user_model().objects.annotate(request_count=Count('care_requests'))


@extend_schema(
    tags=['admin'],
    summary=api_descriptions.ADMIN_USER_LIST_SUMMARY,
    description=api_descriptions.ADMIN_USER_LIST_VIEW_DESCRIPTION,
)
class AdminUserListView(AdminUserQuerysetMixin, generics.ListAPIView):
    __doc__ = api_descriptions.ADMIN_USER_LIST_VIEW_DESCRIPTION

    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['is_staff', 'is_active']
    search_fields = ['email', 'first_name', 'last_name', 'phone']
    ordering_fields = ['date_joined', 'email', 'request_count']
    ordering = ['-date_joined']


@extend_schema(
    tags=['admin'],
    summary=api_descriptions.ADMIN_USER_DETAIL_SUMMARY,
    description=api_descriptions.ADMIN_USER_DETAIL_VIEW_DESCRIPTION,
    parameters=[
        OpenApiParameter(
            'id', OpenApiTypes.INT, OpenApiParameter.PATH,
            description=api_descriptions.ADMIN_USER_ID_PARAMETER_DESCRIPTION,
        ),
    ],
)
class AdminUserDetailView(AdminUserQuerysetMixin, generics.RetrieveAPIView):
    __doc__ = api_descriptions.ADMIN_USER_DETAIL_VIEW_DESCRIPTION
