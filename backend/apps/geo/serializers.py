from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from apps.geo.models import District, Neighborhood


class DistrictSerializer(serializers.ModelSerializer):
    """Form seçimlerindeki bir ilçe."""

    class Meta:
        model = District
        fields = ['id', 'name', 'slug', 'osm_id']
        read_only_fields = fields
        extra_kwargs = {
            'id': {'help_text': _('District identifier; used to list its neighbourhoods.')},
            'name': {'help_text': _('District name as written in Turkish.')},
            'slug': {'help_text': _('ASCII key of the district name.')},
            'osm_id': {'help_text': _('OpenStreetMap relation id; matches the district polygon on the map.')},
        }


class NeighborhoodSerializer(serializers.ModelSerializer):
    """Form seçimlerindeki bir mahalle."""

    class Meta:
        model = Neighborhood
        fields = ['id', 'name', 'osm_id']
        read_only_fields = fields
        extra_kwargs = {
            'id': {'help_text': _('Neighbourhood identifier; sent as the location of applications and inquiries.')},
            'name': {'help_text': _('Neighbourhood name as written in Turkish.')},
            'osm_id': {'help_text': _('OpenStreetMap relation id; matches the neighbourhood polygon on the map.')},
        }


class PlaceSerializer(serializers.Serializer):
    """Bir ilçe veya mahallenin kimliği, adı ve harita kimliği."""

    id = serializers.IntegerField(help_text=_('Identifier of the place.'))
    name = serializers.CharField(help_text=_('Name of the place as written in Turkish.'))
    osm_id = serializers.IntegerField(help_text=_('OpenStreetMap relation id; matches the polygon on the map.'))


class LocationSerializer(serializers.Serializer):
    """Bir mahalleden türetilen konum: mahalle ve bağlı olduğu ilçe."""

    district = PlaceSerializer(help_text=_('District the neighbourhood belongs to.'))
    neighborhood = PlaceSerializer(source='*', help_text=_('Neighbourhood of the service address.'))
