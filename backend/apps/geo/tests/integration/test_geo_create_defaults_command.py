from io import StringIO

from django.core.management import call_command
from django.test import TestCase
from django.utils.translation import gettext

from apps.geo.models import District, Neighborhood

STAR_LINE = '*' * 78
DASH_LINE = '-' * 78


def run_command():
    """
    geo_create_defaults komutunu çalıştırır ve çıktısını satırlarına ayırır.

    Returns:
        list[str]: Komutun standart çıktı satırları.
    """
    out = StringIO()
    call_command('geo_create_defaults', stdout=out, stderr=StringIO())
    return out.getvalue().splitlines()


def summary(created, updated):
    """
    Özet satırını gettext ile üretir.

    Args:
        created (int): Oluşturulan kayıt sayısı.
        updated (int): Güncellenen kayıt sayısı.

    Returns:
        str: Beklenen özet satırı.
    """
    return gettext(
        'All geo default data operations completed. Created: %(created)d, Updated: %(updated)d.'
    ) % {'created': created, 'updated': updated}


class GeoCreateDefaultsTests(TestCase):
    def test_loads_all_districts_and_neighborhoods(self):
        """
        Boş veritabanında tüm ilçe ve mahallelerin yüklendiğini doğrular.

        Senaryo:
        - Hiç kayıt yokken komut çalıştırılır.

        Beklenti:
        - 39 ilçe ve 964 mahalle oluşmalı, özet satırı 1003 oluşturulan kaydı göstermelidir.
        """
        lines = run_command()

        self.assertEqual(District.objects.count(), 39)
        self.assertEqual(Neighborhood.objects.count(), 964)
        self.assertIn(summary(39 + 964, 0), lines)

    def test_second_run_is_idempotent(self):
        """
        Komutun ikinci çalıştırmada kayıt oluşturmadığını ve güncellemediğini doğrular.

        Senaryo:
        - Komut iki kez çalıştırılır.

        Beklenti:
        - Sayılar değişmemeli, ikinci özet Created: 0, Updated: 0 olmalıdır.
        """
        run_command()

        lines = run_command()

        self.assertEqual(District.objects.count(), 39)
        self.assertEqual(Neighborhood.objects.count(), 964)
        self.assertIn(summary(0, 0), lines)

    def test_output_separators(self):
        """
        Çıktı biçiminde ayıraçların doğru yerde ve sayıda olduğunu doğrular.

        Senaryo:
        - Komut çalıştırılır.

        Beklenti:
        - `*` yalnızca ilk ve son satırda, `-` iki kez bulunmalı; adım satırı [1/1] içermelidir.
        """
        lines = run_command()

        self.assertEqual(lines[0], STAR_LINE)
        self.assertEqual(lines[-1], STAR_LINE)
        self.assertEqual(lines.count(STAR_LINE), 2)
        self.assertEqual(lines.count(DASH_LINE), 2)
        self.assertIn('[1/1]', lines[3])
