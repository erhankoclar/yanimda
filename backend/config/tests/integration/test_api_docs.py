from django.test import override_settings

from config.tests.utils import UrlconfReloadTestCase


@override_settings(API_DOCS_ENABLED=True)
class ApiDocsEnabledTests(UrlconfReloadTestCase):
    def test_schema_lists_auth_endpoints_with_jwt_security(self):
        """
        OpenAPI şemasının auth endpoint'lerini ve JWT güvenlik şemasını içerdiğini doğrular.

        Senaryo:
        - Şema endpoint'i JSON formatında, kimlik doğrulamasız çağrılır.

        Beklenti:
        - 200 dönmeli; auth yolları ve `jwtAuth` bearer şeması bulunmalıdır.
        """
        response = self.client.get('/api/schema/', {'format': 'json'})

        self.assertEqual(response.status_code, 200)
        schema = response.json()
        for path in ('/api/auth/register/', '/api/auth/token/', '/api/auth/token/refresh/', '/api/auth/me/'):
            self.assertIn(path, schema['paths'])
        self.assertEqual(schema['components']['securitySchemes']['jwtAuth']['scheme'], 'bearer')

    def test_protected_endpoint_declares_jwt_requirement(self):
        """
        Korumalı endpoint'in şemada JWT gerektirdiğini, kayıt endpoint'inin gerektirmediğini doğrular.

        Senaryo:
        - Şemadan `me` ve `register` operasyonlarının güvenlik tanımları okunur.

        Beklenti:
        - `me` için `jwtAuth` zorunlu olmalı, `register` için olmamalıdır.
        """
        schema = self.client.get('/api/schema/', {'format': 'json'}).json()

        me_security = schema['paths']['/api/auth/me/']['get']['security']
        register_security = schema['paths']['/api/auth/register/']['post'].get('security', [])
        self.assertIn({'jwtAuth': []}, me_security)
        self.assertNotIn({'jwtAuth': []}, register_security)

    def test_swagger_and_redoc_pages_are_served(self):
        """Swagger UI ve ReDoc sayfalarının yayınlandığını doğrular."""
        for url in ('/api/docs/', '/api/redoc/'):
            self.assertEqual(self.client.get(url).status_code, 200)
