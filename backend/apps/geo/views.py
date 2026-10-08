from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import generics, permissions

from apps.geo import api_descriptions
from apps.geo.serializers import DistrictSerializer, NeighborhoodSerializer
from apps.geo.services import location_service


@extend_schema(
    tags=['locations'],
    summary=api_descriptions.DISTRICT_LIST_SUMMARY,
    description=api_descriptions.DISTRICT_LIST_VIEW_DESCRIPTION,
)
class DistrictListView(generics.ListAPIView):
    __doc__ = api_descriptions.DISTRICT_LIST_VIEW_DESCRIPTION

    serializer_class = DistrictSerializer
    permission_classes = [permissions.AllowAny]
    pagination_class = None

    def get_queryset(self):
        """
        İlçeleri servis üzerinden döndürür.

        Returns:
            QuerySet[District]: Sıralı ilçeler.
        """
        return location_service.list_districts()


@extend_schema(
    tags=['locations'],
    summary=api_descriptions.NEIGHBORHOOD_LIST_SUMMARY,
    description=api_descriptions.NEIGHBORHOOD_LIST_VIEW_DESCRIPTION,
    parameters=[OpenApiParameter(
        'district_id', OpenApiTypes.INT, OpenApiParameter.PATH,
        description=api_descriptions.DISTRICT_ID_PARAMETER_DESCRIPTION,
    )],
)
class NeighborhoodListView(generics.ListAPIView):
    __doc__ = api_descriptions.NEIGHBORHOOD_LIST_VIEW_DESCRIPTION

    serializer_class = NeighborhoodSerializer
    permission_classes = [permissions.AllowAny]
    pagination_class = None

    def get_queryset(self):
        """
        Yoldaki ilçenin mahallelerini servis üzerinden döndürür.

        Returns:
            QuerySet[Neighborhood]: Sıralı mahalleler.
        """
        return location_service.list_neighborhoods(self.kwargs['district_id'])
