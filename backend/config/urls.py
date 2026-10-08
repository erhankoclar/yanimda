"""Yanımda API URL yapılandırması."""

from django.conf import settings
from django.urls import include, path, re_path
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView

from config.spa import spa_index

urlpatterns = [
    path('api/auth/', include('apps.accounts.urls')),
    path('api/', include('apps.care.urls')),
    path('api/geo/', include('apps.geo.urls')),
    path('api/admin/', include('apps.care.admin_urls')),
    path('api/admin/', include('apps.accounts.admin_urls')),
]

if settings.API_DOCS_ENABLED:
    urlpatterns += [
        path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
        path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
        path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    ]

# Derlenmiş site varsa API ve statik dosyalar dışındaki tüm adresler Vue uygulamasına gider.
if settings.FRONTEND_DIST_DIR.is_dir():
    urlpatterns += [re_path(r'^(?!api/|static/)(?P<path>.*)$', spa_index, name='spa')]
