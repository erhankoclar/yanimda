"""Proje düzeyindeki testlerde ortak kullanılan yardımcılar."""

import importlib

from django.test import TestCase
from django.urls import clear_url_caches

import config.urls


def reload_urlconf():
    """URL yapılandırmasını etkin ayarlarla yeniden yükler ve URL önbelleğini temizler."""
    clear_url_caches()
    importlib.reload(config.urls)


class UrlconfReloadTestCase(TestCase):
    """Her testten önce ve sonra URL yapılandırmasını etkin ayarlarla yeniden yükler."""

    def setUp(self):
        """Sınıfa uygulanan ayar ezmeleriyle URL yapılandırmasını yükler."""
        reload_urlconf()

    def tearDown(self):
        """Diğer testlerin özgün ayarlarla çalışması için URL yapılandırmasını geri yükler."""
        reload_urlconf()
