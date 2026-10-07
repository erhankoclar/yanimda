from io import StringIO

from django.core.management import call_command
from django.test import SimpleTestCase


class OpenApiSchemaContractTests(SimpleTestCase):
    def test_schema_is_valid_without_warnings(self):
        """
        Üretilen OpenAPI şemasının geçerli olduğunu ve uyarı içermediğini doğrular.

        Senaryo:
        - drf-spectacular şeması doğrulama ve uyarıda hata seçenekleriyle üretilir.

        Beklenti:
        - Komut hata fırlatmamalıdır; frontend ve dış istemciler için sözleşme tutarlı kalmalıdır.
        """
        call_command('spectacular', '--validate', '--fail-on-warn', stdout=StringIO(), stderr=StringIO())

    def test_every_operation_has_summary_and_description(self):
        """
        Her API operasyonunun özet ve açıklamayla belgelendiğini doğrular.

        Senaryo:
        - Şema üretilir ve tüm yol/metot çiftleri gezilir.

        Beklenti:
        - Hiçbir operasyonda `summary` veya `description` boş olmamalıdır.
        """
        from drf_spectacular.generators import SchemaGenerator

        schema = SchemaGenerator().get_schema(request=None, public=True)

        for path, operations in schema['paths'].items():
            for method, operation in operations.items():
                with self.subTest(path=path, method=method):
                    self.assertTrue(operation.get('summary'))
                    self.assertTrue(operation.get('description'))
