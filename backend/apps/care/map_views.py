from drf_spectacular.utils import extend_schema
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.care import api_descriptions
from apps.care.map_serializers import MapQuerySerializer, MapSerializer
from apps.care.services.map_service import build_map


@extend_schema(
    tags=['admin'],
    summary=api_descriptions.ADMIN_MAP_SUMMARY,
    description=api_descriptions.ADMIN_MAP_VIEW_DESCRIPTION,
    parameters=[MapQuerySerializer],
    responses=MapSerializer,
)
class AdminMapView(APIView):
    __doc__ = api_descriptions.ADMIN_MAP_VIEW_DESCRIPTION

    permission_classes = [permissions.IsAdminUser]

    def get(self, request):
        """
        Sorgu parametrelerini doğrular ve ilçe/mahalle bazında sayıları döndürür.

        Args:
            request (Request): Admin kullanıcının isteği; `source` ve `days` parametreleri olabilir.

        Returns:
            Response: MapSerializer şeklinde sayılar.

        Raises:
            ValidationError: `source` veya `days` izin verilen değerlerden biri değilse (400).
        """
        query = MapQuerySerializer(data=request.query_params)
        query.is_valid(raise_exception=True)
        days = query.validated_data.get('days')
        data = build_map(source=query.validated_data['source'], days=int(days) if days else None)
        return Response(MapSerializer(data).data)
