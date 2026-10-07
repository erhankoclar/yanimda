from django.test import SimpleTestCase


class DjangoAdminRemovedTests(SimpleTestCase):
    def test_django_admin_is_not_exposed(self):
        """
        Django yönetim panelinin yayında olmadığını doğrular.

        Senaryo:
        - Varsayılan Django admin adresleri çağrılır.

        Beklenti:
        - Her iki adres de 404 dönmelidir; yönetim ayrı Vue admin panelinden yapılır.
        """
        for url in ('/admin/', '/django-admin/'):
            self.assertEqual(self.client.get(url).status_code, 404)
