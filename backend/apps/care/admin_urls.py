from django.urls import path

from apps.care.admin_views import AdminCareRequestDetailView, AdminCareRequestListView, AdminDashboardStatsView

app_name = 'care-admin'

urlpatterns = [
    path('stats/', AdminDashboardStatsView.as_view(), name='stats'),
    path('requests/', AdminCareRequestListView.as_view(), name='request-list'),
    path('requests/<int:pk>/', AdminCareRequestDetailView.as_view(), name='request-detail'),
]
