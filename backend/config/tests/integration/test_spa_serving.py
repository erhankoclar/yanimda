import tempfile
from pathlib import Path

from django.test import override_settings

from config.tests.utils import UrlconfReloadTestCase

_DIST = Path(tempfile.mkdtemp(prefix='yanimda-dist-'))
(_DIST / 'index.html').write_text('<!doctype html><title>Yanımda SPA</title>', encoding='utf-8')


@override_settings(FRONTEND_DIST_DIR=_DIST)
class SpaServingTests(UrlconfReloadTestCase):
    def test_page_addresses_return_the_spa_entry(self):
        """
        Derlenmiş site varken sayfa adreslerinin Vue giriş dosyasını döndürdüğünü doğrular.

        Senaryo:
        - Kök adres ve doğrudan açılan iç sayfa adresleri istenir.

        Beklenti:
        - Hepsi 200 ve index.html içeriği dönmeli, yanıt önbelleğe alınmamalıdır.
        """
        for path in ('/', '/requests/5', '/admin/requests'):
            with self.subTest(path=path):
                response = self.client.get(path)
                self.assertEqual(response.status_code, 200)
                self.assertIn(b'Yan\xc4\xb1mda SPA', b''.join(response.streaming_content))
                self.assertIn('no-cache', response.headers['Cache-Control'])

    def test_api_addresses_are_not_swallowed_by_the_spa(self):
        """
        Olmayan API adreslerinin SPA'ya düşmeyip 404 döndüğünü doğrular (regresyon).

        Senaryo:
        - Tanımsız bir API adresi istenir.

        Beklenti:
        - 404 dönmeli ve index.html içeriği verilmemelidir.
        """
        response = self.client.get('/api/olmayan-adres/')

        self.assertEqual(response.status_code, 404)
        self.assertNotIn(b'Yan\xc4\xb1mda SPA', response.content)

    def test_api_still_works_next_to_the_spa(self):
        """Derlenmiş site sunulurken API uç noktalarının çalışmaya devam ettiğini doğrular."""
        self.assertEqual(self.client.get('/api/services/').status_code, 200)
