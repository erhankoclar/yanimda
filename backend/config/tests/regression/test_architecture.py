import ast
import importlib
import inspect
from pathlib import Path

from django.conf import settings
from django.test import SimpleTestCase
from rest_framework import serializers

APPS_DIR = Path(settings.BASE_DIR) / 'apps'


def module_files(pattern):
    """
    `apps/` altında, test klasörleri dışında desene uyan Python dosyalarını döndürür.

    Args:
        pattern (str): Dosya adı deseni (ör. `*serializers.py`).

    Returns:
        list[Path]: Eşleşen dosyalar.
    """
    return [path for path in APPS_DIR.rglob(pattern) if 'tests' not in path.parts]


def module_name(path):
    """
    Dosya yolunu içe aktarılabilir modül adına çevirir.

    Args:
        path (Path): Python dosyası.

    Returns:
        str: Modül adı (ör. `apps.care.serializers`).
    """
    relative = path.relative_to(Path(settings.BASE_DIR)).with_suffix('')
    return '.'.join(relative.parts)


class ArchitectureRuleTests(SimpleTestCase):
    """Katman kuralı: iş akışları serviste, serializer yalnızca doğrular, manager yalnızca queryset döndürür."""

    def test_serializers_only_validate(self):
        """
        Hiçbir serializer'ın create veya update ile kayıt yapmadığını doğrular.

        Senaryo:
        - Uygulamalardaki tüm serializer sınıfları taranır.

        Beklenti:
        - Hiçbiri `create` veya `update` metodu tanımlamamalıdır; kaydetme servis katmanındadır.
        """
        offenders = []
        for path in module_files('*serializers.py'):
            module = importlib.import_module(module_name(path))
            for name, cls in inspect.getmembers(module, inspect.isclass):
                if issubclass(cls, serializers.BaseSerializer) and cls.__module__ == module.__name__:
                    offenders += [f'{cls.__module__}.{name}.{method}' for method in ('create', 'update') if method in vars(cls)]

        self.assertEqual(offenders, [])

    def test_views_and_serializers_do_not_build_queries(self):
        """
        View ve serializer'ların ORM sorgularını doğrudan kurmadığını doğrular.

        Senaryo:
        - View ve serializer dosyalarında `.objects.` erişimi aranır; seçim alanı kaynakları için
          yalnızca manager metodu (`.objects.active()`) kullanımına izin verilir.

        Beklenti:
        - Okuma ve yazma işlemleri servis fonksiyonları üzerinden yapılmalıdır.
        """
        offenders = []
        for pattern in ('*views.py', '*serializers.py'):
            for path in module_files(pattern):
                for number, line in enumerate(path.read_text(encoding='utf-8').splitlines(), start=1):
                    if '.objects.' in line and '.objects.active()' not in line:
                        offenders.append(f'{path.name}:{number}: {line.strip()}')

        self.assertEqual(offenders, [])

    def test_managers_do_not_import_services_at_module_level(self):
        """
        Manager modüllerinin servisleri modül düzeyinde içe aktarmadığını doğrular (döngüsel import koruması).

        Senaryo:
        - `managers.py` dosyalarının en üst düzey import'ları okunur.

        Beklenti:
        - Hiçbiri `services` paketini içe aktarmamalıdır.
        """
        offenders = []
        for path in module_files('managers.py'):
            tree = ast.parse(path.read_text(encoding='utf-8'))
            for node in tree.body:
                if isinstance(node, (ast.Import, ast.ImportFrom)):
                    names = [node.module or ''] + [alias.name for alias in node.names]
                    if any('services' in name for name in names):
                        offenders.append(f'{path}: {ast.unparse(node)}')

        self.assertEqual(offenders, [])
