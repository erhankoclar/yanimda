from django.urls import path

from apps.geo.views import DistrictListView, NeighborhoodListView

app_name = 'geo'

urlpatterns = [
    path('districts/', DistrictListView.as_view(), name='district-list'),
    path('districts/<int:district_id>/neighborhoods/', NeighborhoodListView.as_view(), name='neighborhood-list'),
]
