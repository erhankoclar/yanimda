from django.urls import path

from apps.care.admin_views import AdminCareRequestDetailView, AdminCareRequestListView

app_name = 'care-admin'

urlpatterns = [
    path('requests/', AdminCareRequestListView.as_view(), name='request-list'),
    path('requests/<int:pk>/', AdminCareRequestDetailView.as_view(), name='request-detail'),
]
