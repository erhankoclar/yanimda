from django.urls import path

from apps.care.admin_views import AdminCareRequestDetailView, AdminCareRequestListView, AdminDashboardStatsView
from apps.care.inquiry_views import AdminServiceInquiryListView

app_name = 'care-admin'

urlpatterns = [
    path('stats/', AdminDashboardStatsView.as_view(), name='stats'),
    path('requests/', AdminCareRequestListView.as_view(), name='request-list'),
    path('inquiries/', AdminServiceInquiryListView.as_view(), name='inquiry-list'),
    path('requests/<int:pk>/', AdminCareRequestDetailView.as_view(), name='request-detail'),
]
