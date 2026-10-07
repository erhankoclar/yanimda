from django.db import connection
from django.test import SimpleTestCase


class DatabaseEngineTests(SimpleTestCase):
    def test_project_runs_on_postgresql(self):
        """
        Projenin PostgreSQL ile çalıştığını, SQLite'a geri dönülmediğini doğrular.

        Senaryo:
        - Etkin veritabanı bağlantısının sürücüsü okunur.

        Beklenti:
        - Sürücü `postgresql` olmalıdır; testler üretimle aynı veritabanı türünde koşmalıdır.
        """
        self.assertEqual(connection.vendor, 'postgresql')
