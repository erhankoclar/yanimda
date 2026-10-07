from io import StringIO
from unittest.mock import patch

from django.core.management import call_command
from django.test import TestCase
from django.utils.translation import gettext

from apps.care.defaults import DEFAULT_SERVICE_TYPES
from apps.care.models import ServiceType

STAR_LINE = '*' * 78
DASH_LINE = '-' * 78


def run_command():
    """
    care_create_defaults komutunu çalıştırır ve çıktısını satırlarına ayırır.

    Returns:
        list[str]: Komutun standart çıktı satırları.
    """
    out = StringIO()
    call_command('care_create_defaults', stdout=out, stderr=StringIO())
    return out.getvalue().splitlines()


class CareCreateDefaultsTests(TestCase):
    def test_creates_default_service_types_on_empty_database(self):
        """
        Boş veritabanında varsayılan hizmet türlerinin oluşturulduğunu doğrular.

        Senaryo:
        - Hiç hizmet türü yokken komut çalıştırılır.

        Beklenti:
        - Tüm varsayılan hizmetler oluşmalı ve özet satırı oluşturulan sayıyı göstermelidir.
        """
        lines = run_command()

        self.assertEqual(ServiceType.objects.count(), len(DEFAULT_SERVICE_TYPES))
        expected = gettext(
            'All care default data operations completed. Created: %(created)d, Updated: %(updated)d.'
        ) % {'created': len(DEFAULT_SERVICE_TYPES), 'updated': 0}
        self.assertIn(expected, lines)

    def test_second_run_is_idempotent(self):
        """
        Komutun ikinci çalıştırmada kayıt oluşturmadığını ve güncellemediğini doğrular.

        Senaryo:
        - Komut iki kez çalıştırılır.

        Beklenti:
        - Kayıt sayısı değişmemeli, ikinci özet 0/0 göstermelidir.
        """
        run_command()

        lines = run_command()

        self.assertEqual(ServiceType.objects.count(), len(DEFAULT_SERVICE_TYPES))
        expected = gettext(
            'All care default data operations completed. Created: %(created)d, Updated: %(updated)d.'
        ) % {'created': 0, 'updated': 0}
        self.assertIn(expected, lines)

    def test_changed_default_is_updated(self):
        """
        Varsayılandan farklılaşmış kaydın güncellendiğini doğrular.

        Senaryo:
        - Komut çalıştırılır, bir hizmetin açıklaması değiştirilir.
        - Komut tekrar çalıştırılır.

        Beklenti:
        - Açıklama varsayılana dönmeli ve güncellenen sayısı 1 olmalıdır.
        """
        run_command()
        ServiceType.objects.filter(slug='refakat').update(description='eski')

        lines = run_command()

        default = next(item for item in DEFAULT_SERVICE_TYPES if item['slug'] == 'refakat')
        self.assertEqual(ServiceType.objects.get(slug='refakat').description, default['description'])
        expected = gettext(
            'All care default data operations completed. Created: %(created)d, Updated: %(updated)d.'
        ) % {'created': 0, 'updated': 1}
        self.assertIn(expected, lines)

    def test_output_separators(self):
        """
        Çıktı biçiminde ayıraçların doğru yerde ve sayıda olduğunu doğrular.

        Senaryo:
        - Komut tek veri grubuyla çalıştırılır.

        Beklenti:
        - `*` ayıracı yalnızca ilk ve son satırda, `-` ayıracı iki kez bulunmalıdır.
        """
        lines = run_command()

        self.assertEqual(lines[0], STAR_LINE)
        self.assertEqual(lines[-1], STAR_LINE)
        self.assertEqual(lines.count(STAR_LINE), 2)
        self.assertEqual(lines.count(DASH_LINE), 2)
        self.assertIn('[1/1]', lines[3])

    def test_failure_closes_block_and_reraises(self):
        """
        Hata durumunda dış bloğun kapatıldığını ve exception'ın iletildiğini doğrular (hata yolu).

        Senaryo:
        - Hizmet türü oluşturma adımı hata fırlatacak şekilde değiştirilir.

        Beklenti:
        - Exception çağırana ulaşmalı, son satır `*` ayıracı olmalıdır.
        """
        out = StringIO()
        with patch('apps.care.models.ServiceType.objects.get_or_create', side_effect=RuntimeError('boom')):
            with self.assertRaises(RuntimeError):
                call_command('care_create_defaults', stdout=out, stderr=StringIO())

        lines = out.getvalue().splitlines()
        self.assertEqual(lines[-1], STAR_LINE)
        self.assertEqual(lines.count(STAR_LINE), 2)
