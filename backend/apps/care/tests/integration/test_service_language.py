from django.urls import reverse
from rest_framework.test import APITestCase

from apps.care.tests.factories import make_service


class ServiceLanguageTests(APITestCase):
    def setUp(self):
        """Biri İngilizce karşılıklı, biri yalnızca Türkçe iki hizmet hazırlar."""
        make_service(
            name='Refakat', description='Düzenli ziyaret', name_en='Companionship', description_en='Regular visits',
            sort_order=1,
        )
        make_service(name='Küçük tamir', description='Ampul ve musluk', sort_order=2)

    def names(self, language):
        """
        Hizmet listesini verilen dilde ister.

        Args:
            language (str): Accept-Language başlığı.

        Returns:
            list[tuple[str, str]]: (ad, açıklama) çiftleri.
        """
        data = self.client.get(reverse('care:service-list'), HTTP_ACCEPT_LANGUAGE=language).data
        return [(item['name'], item['description']) for item in data]

    def test_english_request_returns_english_texts(self):
        """
        İngilizce istekte hizmetlerin İngilizce ad ve açıklamayla döndüğünü doğrular.

        Senaryo:
        - Hizmet listesi `Accept-Language: en` ile istenir.

        Beklenti:
        - İngilizce karşılığı olan hizmet İngilizce, olmayan Türkçe dönmelidir (yedek).
        """
        self.assertEqual(self.names('en'), [('Companionship', 'Regular visits'), ('Küçük tamir', 'Ampul ve musluk')])

    def test_turkish_request_returns_turkish_texts(self):
        """Türkçe istekte hizmetlerin Türkçe ad ve açıklamayla döndüğünü doğrular."""
        self.assertEqual(self.names('tr'), [('Refakat', 'Düzenli ziyaret'), ('Küçük tamir', 'Ampul ve musluk')])

    def test_default_services_have_english_texts(self):
        """
        Varsayılan hizmetlerin hepsinin İngilizce karşılığı olduğunu doğrular (eksik çeviri regresyonu).

        Senaryo:
        - Varsayılan veri tanımları okunur.

        Beklenti:
        - Her hizmette `name_en` ve `description_en` dolu olmalıdır.
        """
        from apps.care.defaults import DEFAULT_SERVICE_TYPES

        for item in DEFAULT_SERVICE_TYPES:
            with self.subTest(slug=item['slug']):
                self.assertTrue(item['name_en'] and item['description_en'])
