from django.urls import path

from apps.care.admin_views import AdminCareRequestListView

app_name = 'care-admin'

urlpatterns = [
    path('requests/', AdminCareRequestListView.as_view(), name='request-list'),
]
