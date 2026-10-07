from django.urls import path

from apps.accounts.admin_views import AdminUserDetailView, AdminUserListView

app_name = 'accounts-admin'

urlpatterns = [
    path('users/', AdminUserListView.as_view(), name='user-list'),
    path('users/<int:pk>/', AdminUserDetailView.as_view(), name='user-detail'),
]
