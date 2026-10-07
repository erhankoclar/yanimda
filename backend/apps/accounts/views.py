from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import generics, permissions
from rest_framework_simplejwt.views import TokenBlacklistView, TokenObtainPairView, TokenRefreshView

from apps.accounts import api_descriptions
from apps.accounts.serializers import RegisterSerializer, UserSerializer
from apps.accounts.throttles import LoginRateThrottle, RegisterRateThrottle


@extend_schema(
    tags=['auth'],
    summary=api_descriptions.REGISTER_SUMMARY,
    description=api_descriptions.REGISTER_VIEW_DESCRIPTION,
)
class RegisterView(generics.CreateAPIView):
    __doc__ = api_descriptions.REGISTER_VIEW_DESCRIPTION

    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]
    authentication_classes = []
    throttle_classes = [RegisterRateThrottle]


@extend_schema(
    tags=['auth'],
    summary=api_descriptions.TOKEN_OBTAIN_SUMMARY,
    description=api_descriptions.TOKEN_OBTAIN_VIEW_DESCRIPTION,
)
class LoginView(TokenObtainPairView):
    __doc__ = api_descriptions.TOKEN_OBTAIN_VIEW_DESCRIPTION

    throttle_classes = [LoginRateThrottle]


@extend_schema(
    tags=['auth'],
    summary=api_descriptions.TOKEN_REFRESH_SUMMARY,
    description=api_descriptions.TOKEN_REFRESH_VIEW_DESCRIPTION,
)
class RefreshView(TokenRefreshView):
    __doc__ = api_descriptions.TOKEN_REFRESH_VIEW_DESCRIPTION


@extend_schema(
    tags=['auth'],
    summary=api_descriptions.LOGOUT_SUMMARY,
    description=api_descriptions.LOGOUT_VIEW_DESCRIPTION,
)
class LogoutView(TokenBlacklistView):
    __doc__ = api_descriptions.LOGOUT_VIEW_DESCRIPTION


@extend_schema_view(
    get=extend_schema(
        tags=['auth'], summary=api_descriptions.ME_SUMMARY, description=api_descriptions.ME_VIEW_DESCRIPTION,
    ),
    patch=extend_schema(
        tags=['auth'], summary=api_descriptions.ME_SUMMARY, description=api_descriptions.ME_VIEW_DESCRIPTION,
    ),
)
class MeView(generics.RetrieveUpdateAPIView):
    __doc__ = api_descriptions.ME_VIEW_DESCRIPTION

    serializer_class = UserSerializer
    http_method_names = ['get', 'patch', 'head', 'options']

    def get_object(self):
        """
        İşlem yapılacak nesne olarak oturum açmış kullanıcıyı döndürür.

        Returns:
            User: İsteği yapan kullanıcı.
        """
        return self.request.user
