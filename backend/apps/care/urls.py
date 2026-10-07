from django.urls import path

from apps.care.views import CareRequestDetailView, CareRequestListCreateView, ServiceTypeListView

app_name = 'care'

urlpatterns = [
    path('services/', ServiceTypeListView.as_view(), name='service-list'),
    path('requests/', CareRequestListCreateView.as_view(), name='request-list'),
    path('requests/<int:pk>/', CareRequestDetailView.as_view(), name='request-detail'),
]
