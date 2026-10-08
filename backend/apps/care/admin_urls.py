from django.urls import path

from apps.care.admin_views import (
    AdminCareRequestDetailView,
    AdminCareRequestListView,
    AdminDashboardStatsView,
    AdminDashboardView,
)
from apps.care.inquiry_views import AdminServiceInquiryDetailView, AdminServiceInquiryListView
from apps.care.map_views import AdminMapView

app_name = 'care-admin'

urlpatterns = [
    path('dashboard/', AdminDashboardView.as_view(), name='dashboard'),
    path('stats/', AdminDashboardStatsView.as_view(), name='stats'),
    path('map/', AdminMapView.as_view(), name='map'),
    path('requests/', AdminCareRequestListView.as_view(), name='request-list'),
    path('inquiries/', AdminServiceInquiryListView.as_view(), name='inquiry-list'),
    path('inquiries/<int:pk>/', AdminServiceInquiryDetailView.as_view(), name='inquiry-detail'),
    path('requests/<int:pk>/', AdminCareRequestDetailView.as_view(), name='request-detail'),
]
