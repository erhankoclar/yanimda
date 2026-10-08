import importlib
from types import SimpleNamespace
from unittest import TestCase

migration = importlib.import_module('apps.care.migrations.0010_add_neighborhood_location')


class FakeRow:
    """Migration fonksiyonlarının dokunduğu alanları taşıyan, kaydedilen alanları not eden sahte kayıt."""

    def __init__(self, address, city='', district='', neighborhood=None):
        """
        Sahte kaydı oluşturur.

        Args:
            address (str): Mevcut adres.
            city (str): Eski il metni.
            district (str): Eski ilçe metni.
            neighborhood (Optional[Any]): Mahalle (geri alma için).
        """
        self.address = address
        self.city = city
        self.district = district
        self.neighborhood = neighborhood
        self.saved = []

    def save(self, update_fields):
        """
        Kaydedilen alan adlarını not eder.

        Args:
            update_fields (list[str]): Kaydedilen alanlar.
        """
        self.saved.append(update_fields)


class FakeManager:
    """`exclude` ve `select_related` zincirini taklit eden sahte manager."""

    def __init__(self, rows):
        """
        Args:
            rows (list[FakeRow]): Manager'ın döndüreceği kayıtlar.
        """
        self.rows = rows

    def exclude(self, **conditions):
        """
        Verilen eşitliklerin hepsini sağlayan kayıtları eler.

        Args:
            **conditions (Any): Elenecek eşitlikler.

        Returns:
            list[FakeRow]: Kalan kayıtlar.
        """
        return [
            row for row in self.rows
            if not all(getattr(row, field) == value for field, value in conditions.items())
        ]

    def select_related(self, *_args):
        """
        Zincirin devamı için kayıtları döndürür.

        Returns:
            list[FakeRow]: Tüm kayıtlar.
        """
        return self.rows


def fake_apps(rows):
    """
    `apps.get_model('care', 'CareRequest')` çağrısını yanıtlayan sahte uygulama kaydı üretir.

    Args:
        rows (list[FakeRow]): Sahte modelin kayıtları.

    Returns:
        SimpleNamespace: `get_model` metodu olan nesne.
    """
    model = SimpleNamespace(objects=FakeManager(rows))
    return SimpleNamespace(get_model=lambda app, name: model)


class LocationMigrationTests(TestCase):
    """0010 migration'ının eski il/ilçe metnini kaybetmeden adrese taşıdığını sınar."""

    def test_city_and_district_are_appended_to_address(self):
        """
        Eski il ve ilçe metninin adresin sonuna eklendiğini doğrular.

        Senaryo:
        - İl ve ilçesi dolu, yalnızca ili dolu ve ikisi de boş üç kayıtla veri taşıma fonksiyonu çalıştırılır.

        Beklenti:
        - Dolu olanların adresi "adres, ilçe / il" biçimine gelmeli, boş olana dokunulmamalıdır.
        """
        full = FakeRow('Örnek Sok. No: 1', city='Samsun', district='İlkadım')
        city_only = FakeRow('Deneme Cad. No: 2', city='Ankara')
        empty = FakeRow('Boş Sok. No: 3')

        migration.move_city_district_into_address(fake_apps([full, city_only, empty]), None)

        self.assertEqual(full.address, 'Örnek Sok. No: 1, İlkadım / Samsun')
        self.assertEqual(city_only.address, 'Deneme Cad. No: 2, Ankara')
        self.assertEqual(empty.address, 'Boş Sok. No: 3')
        self.assertEqual(full.saved, [['address']])
        self.assertEqual(empty.saved, [])

    def test_reverse_restores_city_and_district_from_neighborhood(self):
        """
        Geri almada ilin İstanbul, ilçenin mahallenin ilçesi olarak yazıldığını doğrular.

        Senaryo:
        - Biri mahalleli, biri mahallesiz iki kayıtla geri alma fonksiyonu çalıştırılır.

        Beklenti:
        - Mahalleli kayıtta ilçe adı yazılmalı, mahallesizde ilçe boş kalmalı; il İstanbul olmalıdır.
        """
        neighborhood = SimpleNamespace(district=SimpleNamespace(name='Kadıköy'))
        located = FakeRow('A', neighborhood=neighborhood)
        old = FakeRow('B')

        migration.restore_city_district(fake_apps([located, old]), None)

        self.assertEqual((located.city, located.district), ('İstanbul', 'Kadıköy'))
        self.assertEqual((old.city, old.district), ('İstanbul', ''))
