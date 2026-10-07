from io import StringIO

from django.core.management import call_command
from django.test import TestCase


class MigrationConsistencyTests(TestCase):
    def test_models_have_no_missing_migrations(self):
        """
        Model değişikliklerinin migration dosyalarına yansıtıldığını doğrular.

        Senaryo:
        - `makemigrations --check --dry-run` çalıştırılır.

        Beklenti:
        - Eksik migration olmamalıdır; aksi halde komut SystemExit fırlatır.
        """
        call_command('makemigrations', '--check', '--dry-run', stdout=StringIO(), stderr=StringIO())
