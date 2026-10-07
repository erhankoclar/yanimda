from django.test import SimpleTestCase

from apps.care.text import person_name_key


class PersonNameKeyTests(SimpleTestCase):
    def test_turkish_i_variants_and_case_produce_same_key(self):
        """
        Türkçe i varyantları ve büyük/küçük harf farkının aynı anahtarı ürettiğini doğrular.

        Senaryo:
        - Aynı ad; büyük harf, Türkçe karakterli, Türkçe karaktersiz ve İ'li yazımlarla anahtara çevrilir.

        Beklenti:
        - Tüm yazımlar aynı anahtarı vermelidir.
        """
        variants = ['Fatma Yılmaz', 'FATMA YILMAZ', 'fatma yilmaz', 'Fatma Yilmaz']
        self.assertEqual({person_name_key(value) for value in variants}, {'fatma yilmaz'})
        self.assertEqual(person_name_key('İNCE'), person_name_key('ince'))

    def test_whitespace_is_collapsed(self):
        """Baştaki/sondaki ve ardışık boşlukların anahtarı etkilemediğini doğrular."""
        self.assertEqual(person_name_key('  Fatma   Yılmaz '), 'fatma yilmaz')

    def test_different_names_produce_different_keys(self):
        """Farklı kişilerin farklı anahtar ürettiğini doğrular."""
        self.assertNotEqual(person_name_key('Fatma Yılmaz'), person_name_key('Fatma Yıldız'))
