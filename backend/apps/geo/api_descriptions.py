"""geo uç noktalarının özet ve ayrıntılı açıklamaları (Swagger ve URL kaynakları için tek kaynak)."""

from django.utils.translation import gettext_lazy as _

DISTRICT_LIST_SUMMARY = _('List districts')
DISTRICT_LIST_VIEW_DESCRIPTION = _(
    '<p>Lists the districts of Istanbul, where the service is offered, in Turkish alphabetical order. '
    'No authentication is required.</p>'
    '<p>The application and quick inquiry forms show these districts first; the neighbourhoods of the chosen '
    'district come from <a href="#operations-locations-geo_districts_neighborhoods_list">List neighbourhoods '
    'of a district</a>.</p>'
)
DISTRICT_LIST_URL_DESCRIPTION = _(
    '<p>Lists the districts of Istanbul, where the service is offered, in Turkish alphabetical order. '
    'No authentication is required.</p>'
    '<p>The application and quick inquiry forms show these districts first; the neighbourhoods of the chosen '
    'district come from the "List neighbourhoods of a district" service.</p>'
)

NEIGHBORHOOD_LIST_SUMMARY = _('List neighbourhoods of a district')
NEIGHBORHOOD_LIST_VIEW_DESCRIPTION = _(
    '<p>Lists the neighbourhoods of one district in Turkish alphabetical order. No authentication is required.</p>'
    '<p>An unknown district returns an empty list.</p>'
)
NEIGHBORHOOD_LIST_URL_DESCRIPTION = _(
    '<p>Lists the neighbourhoods of one district in Turkish alphabetical order. No authentication is required.</p>'
    '<p>An unknown district returns an empty list.</p>'
)

DISTRICT_ID_PARAMETER_DESCRIPTION = _(
    'District identifier. Copy it from <a href="#operations-locations-geo_districts_list">List districts</a> '
    '— <code>[].id</code>.'
)
