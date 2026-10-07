from django.test import override_settings

from config.tests.utils import UrlconfReloadTestCase


@override_settings(API_DOCS_ENABLED=False)
class ApiDocsDisabledTests(UrlconfReloadTestCase):
    def test_docs_are_hidden_when_disabled(self):
        """
        Dokümantasyon kapalıyken şema ve arayüzlerin yayınlanmadığını doğrular.

        Senaryo:
        - `API_DOCS_ENABLED=False` ile şema, Swagger ve ReDoc adresleri çağrılır.

        Beklenti:
        - Hepsi 404 dönmeli; API yapısı üretimde dışarı açılmamalıdır.
        """
        for url in ('/api/schema/', '/api/docs/', '/api/redoc/'):
            self.assertEqual(self.client.get(url).status_code, 404)
