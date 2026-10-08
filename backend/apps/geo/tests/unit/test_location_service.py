from django.test import SimpleTestCase, TestCase

from apps.geo.models import District, Neighborhood
from apps.geo.services.location_service import create_default_locations, turkish_sort_key


def make_data():
    """
    Küçük, sırası bilerek karışık bir ilçe ağacı üretir.

    Returns:
        list[dict]: İki ilçe ve üç mahalle içeren veri.
    """
    return [
        {'osm_id': 2, 'name': 'Çatalca', 'slug': 'catalca', 'neighborhoods': [
            {'osm_id': 21, 'name': 'Zeytinburnu Mahallesi'},
            {'osm_id': 22, 'name': 'Ağaçlı Mahallesi'},
        ]},
        {'osm_id': 1, 'name': 'Bağcılar', 'slug': 'bagcilar', 'neighborhoods': [
            {'osm_id': 11, 'name': 'Çınar Mahallesi'},
        ]},
    ]


class TurkishSortKeyTests(SimpleTestCase):
    def test_g_breaks_before_h(self):
        """
        'Bağcılar' adının 'Bahçelievler' adından önce sıralandığını doğrular.

        Senaryo:
        - İki ilçe adı için sıra anahtarı üretilir.

        Beklenti:
        - 'Bağcılar' anahtarı 'Bahçelievler' anahtarından küçük olmalıdır.
        """
        self.assertLess(turkish_sort_key('Bağcılar'), turkish_sort_key('Bahçelievler'))

    def test_c_cedilla_after_c_before_d(self):
        """
        'Ç' harfinin 'C' sonrasında ve 'D' öncesinde sıralandığını doğrular.

        Senaryo:
        - Büyükçekmece, Çatalca ve Esenler adları karışık sıralanır.

        Beklenti:
        - Sıra Büyükçekmece, Çatalca, Esenler olmalıdır.
        """
        self.assertEqual(
            sorted(['Esenler', 'Çatalca', 'Büyükçekmece'], key=turkish_sort_key),
            ['Büyükçekmece', 'Çatalca', 'Esenler'],
        )

    def test_u_umlaut_after_t(self):
        """
        'Ü' harfinin 'T' sonrasında sıralandığını doğrular.

        Senaryo:
        - Ümraniye ve Tuzla adları karşılaştırılır.

        Beklenti:
        - 'Tuzla' 'Ümraniye' adından önce gelmelidir.
        """
        self.assertLess(turkish_sort_key('Tuzla'), turkish_sort_key('Ümraniye'))

    def test_dotless_i_before_dotted_i(self):
        """
        Noktasız 'ı' harfinin noktalı 'i' harfinden önce geldiğini doğrular.

        Senaryo:
        - 'Işık', 'İstanbul' ve 'ılık' / 'ilk' çiftleri karşılaştırılır.

        Beklenti:
        - Büyük 'I' noktasız, büyük 'İ' noktalı harf sayılarak sıralanmalıdır.
        """
        self.assertLess(turkish_sort_key('Işık'), turkish_sort_key('İstanbul'))
        self.assertLess(turkish_sort_key('ılık'), turkish_sort_key('ilk'))
        self.assertEqual(turkish_sort_key('I'), turkish_sort_key('ı'))
        self.assertEqual(turkish_sort_key('İ'), turkish_sort_key('i'))

    def test_full_alphabet_order(self):
        """
        Türkçe alfabenin tüm harflerinin doğru sırada olduğunu doğrular.

        Senaryo:
        - Her harften oluşan tek harfli adlar ters sırayla verilir.

        Beklenti:
        - Sıralama Türkçe alfabe sırası olmalıdır.
        """
        alphabet = list('abcçdefgğhıijklmnoöprsştuüvyz')

        self.assertEqual(sorted(reversed(alphabet), key=turkish_sort_key), alphabet)


class CreateDefaultLocationsTests(TestCase):
    def test_creates_rows_with_turkish_sort_order(self):
        """
        İlçe ve mahallelerin Türkçe sıra numarasıyla oluşturulduğunu doğrular.

        Senaryo:
        - Boş veritabanında küçük bir veri listesiyle servis çalıştırılır.

        Beklenti:
        - 2 ilçe, 3 mahalle oluşmalı; sort_order Türkçe alfabeye göre 1 ile başlamalıdır.
        """
        result = create_default_locations(make_data())

        self.assertEqual(result, {'created': 5, 'updated': 0})
        self.assertEqual(District.objects.get(osm_id=1).sort_order, 1)
        self.assertEqual(District.objects.get(osm_id=2).sort_order, 2)
        self.assertEqual(Neighborhood.objects.get(osm_id=22).sort_order, 1)
        self.assertEqual(Neighborhood.objects.get(osm_id=21).sort_order, 2)
        self.assertEqual(Neighborhood.objects.get(osm_id=22).district.osm_id, 2)

    def test_second_run_changes_nothing(self):
        """
        Servisin ikinci çalıştırmada hiçbir kaydı oluşturmadığını ve güncellemediğini doğrular.

        Senaryo:
        - Aynı veriyle servis iki kez çalıştırılır.

        Beklenti:
        - İkinci sonuç created 0, updated 0 olmalıdır.
        """
        create_default_locations(make_data())

        result = create_default_locations(make_data())

        self.assertEqual(result, {'created': 0, 'updated': 0})
        self.assertEqual(District.objects.count(), 2)
        self.assertEqual(Neighborhood.objects.count(), 3)

    def test_changed_name_updates_only_that_row(self):
        """
        Değişen bir adın yalnızca ilgili satırı güncellediğini doğrular.

        Senaryo:
        - Veri yüklenir, bir mahallenin adı değiştirilip tekrar yüklenir.

        Beklenti:
        - updated 1 olmalı ve ad yeni değere dönüşmelidir.
        """
        create_default_locations(make_data())
        data = make_data()
        data[1]['neighborhoods'][0]['name'] = 'Yeni Çınar Mahallesi'

        result = create_default_locations(data)

        self.assertEqual(result, {'created': 0, 'updated': 1})
        self.assertEqual(Neighborhood.objects.get(osm_id=11).name, 'Yeni Çınar Mahallesi')

    def test_moved_neighborhood_updates_district(self):
        """
        Başka ilçeye taşınan mahallenin ilçe bağının güncellendiğini doğrular.

        Senaryo:
        - Veri yüklenir, bir mahalle diğer ilçenin listesine taşınıp tekrar yüklenir.

        Beklenti:
        - Mahalle yeni ilçeye bağlanmalı; tekrar oluşturulmamalıdır.
        """
        create_default_locations(make_data())
        data = make_data()
        moved = data[1]['neighborhoods'].pop()
        data[0]['neighborhoods'].append(moved)

        result = create_default_locations(data)

        self.assertEqual(result['created'], 0)
        self.assertGreaterEqual(result['updated'], 1)
        self.assertEqual(Neighborhood.objects.get(osm_id=11).district.osm_id, 2)
        self.assertEqual(Neighborhood.objects.count(), 3)
