from django.urls import path

from apps.accounts.views import LoginView, MeView, RefreshView, RegisterView

app_name = 'accounts'

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('token/', LoginView.as_view(), name='token'),
    path('token/refresh/', RefreshView.as_view(), name='token-refresh'),
    path('me/', MeView.as_view(), name='me'),
]
