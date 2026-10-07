"""Derlenmiş Vue sitesini (tek sayfa uygulaması) sunan görünüm."""

from django.conf import settings
from django.http import FileResponse, Http404
from django.views.decorators.cache import never_cache


@never_cache
def spa_index(request, path=''):
    """
    Vue yönlendiricisinin işleyeceği her sayfa adresi için index.html döndürür.

    `/requests/5` gibi doğrudan açılan veya yenilenen adresler sunucuda dosya
    olarak bulunmadığından tek sayfa uygulamasının giriş dosyası verilir.
    Önbelleğe alınmaz; böylece yeni yayınlar hemen görünür.

    Args:
        request (HttpRequest): Gelen istek.
        path (str): İstenen yol; yalnızca URL eşleşmesi için alınır.

    Returns:
        FileResponse: index.html içeriği.

    Raises:
        Http404: Derlenmiş site bulunamazsa.
    """
    index = settings.FRONTEND_DIST_DIR / 'index.html'
    if not index.is_file():
        raise Http404('Frontend build not found.')
    return FileResponse(index.open('rb'), content_type='text/html; charset=utf-8')
