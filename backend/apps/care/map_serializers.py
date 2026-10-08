from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from apps.care import api_descriptions
from apps.care.services.map_service import SOURCES


class MapQuerySerializer(serializers.Serializer):
    """Tematik harita sorgu parametrelerini doğrular."""

    source = serializers.ChoiceField(
        choices=SOURCES, default='all', help_text=api_descriptions.ADMIN_MAP_SOURCE_HELP_TEXT,
    )
    days = serializers.ChoiceField(
        choices=[30, 90, 365], required=False, help_text=api_descriptions.ADMIN_MAP_DAYS_HELP_TEXT,
    )


class MapServiceCountSerializer(serializers.Serializer):
    id = serializers.IntegerField(help_text=_('Identifier of the service type; the key used in <code>by_service</code>.'))
    name = serializers.CharField(help_text=_('Service name in the request language.'))
    icon = serializers.CharField(help_text=_('Icon key of the service type.'))
    count = serializers.IntegerField(help_text=_('Records of this service with a location.'))


class MapAreaSerializer(serializers.Serializer):
    id = serializers.IntegerField(help_text=_('District or neighbourhood identifier; used by the list filters.'))
    osm_id = serializers.IntegerField(help_text=_('OpenStreetMap relation id; matches the polygon in the boundary files.'))
    name = serializers.CharField(help_text=_('Name of the area as written in Turkish.'))
    count = serializers.IntegerField(help_text=_('Records in the area.'))
    by_service = serializers.DictField(
        child=serializers.IntegerField(),
        help_text=_('Records per service: service id (as text) to count. Services without records are left out.'),
    )


class MapNeighborhoodSerializer(MapAreaSerializer):
    district_id = serializers.IntegerField(help_text=_('Identifier of the district the neighbourhood belongs to.'))


class MapSerializer(serializers.Serializer):
    """Tematik harita yanıtının şekli."""

    total = serializers.IntegerField(help_text=_('All counted records with a location in Istanbul.'))
    services = MapServiceCountSerializer(many=True, help_text=_('Active services with their counts.'))
    districts = MapAreaSerializer(many=True, help_text=_('Every district, also with zero records.'))
    neighborhoods = MapNeighborhoodSerializer(many=True, help_text=_('Neighbourhoods with at least one record, most first.'))
