from django.urls import reverse
from rest_framework.test import APITestCase

from apps.care.tests.factories import make_service


class ServiceLanguageTests(APITestCase):
    def setUp(self):
        """Biri İngilizce çevirili, biri yalnızca Türkçe iki hizmet hazırlar."""
        companion = make_service(name='Refakat', description='Düzenli ziyaret', sort_order=1)
        companion.set_current_language('en')
        companion.name = 'Companionship'
        companion.description = 'Regular visits'
        companion.save()
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
        - İngilizce çevirisi olan hizmet İngilizce, olmayan Türkçe dönmelidir (yedek dil).
        """
        self.assertEqual(self.names('en'), [('Companionship', 'Regular visits'), ('Küçük tamir', 'Ampul ve musluk')])

    def test_turkish_request_returns_turkish_texts(self):
        """Türkçe istekte hizmetlerin Türkçe ad ve açıklamayla döndüğünü doğrular."""
        self.assertEqual(self.names('tr'), [('Refakat', 'Düzenli ziyaret'), ('Küçük tamir', 'Ampul ve musluk')])

    def test_unsupported_language_falls_back_to_turkish(self):
        """
        Desteklenmeyen dilde hizmetlerin Türkçe döndüğünü doğrular (uç durum).

        Senaryo:
        - Hizmet listesi `Accept-Language: de` ile istenir.

        Beklenti:
        - Tüm hizmetler varsayılan dil olan Türkçe ad ve açıklamayla dönmelidir.
        """
        self.assertEqual(self.names('de'), [('Refakat', 'Düzenli ziyaret'), ('Küçük tamir', 'Ampul ve musluk')])

    def test_default_services_have_english_texts(self):
        """
        Varsayılan hizmetlerin hepsinin İngilizce çevirisi olduğunu doğrular (eksik çeviri regresyonu).

        Senaryo:
        - Varsayılan veri tanımları okunur.

        Beklenti:
        - Her hizmetin `tr` ve `en` çevirisinde ad ve açıklama dolu olmalıdır.
        """
        from apps.care.defaults import DEFAULT_SERVICE_TYPES

        for item in DEFAULT_SERVICE_TYPES:
            for language in ('tr', 'en'):
                with self.subTest(slug=item['slug'], language=language):
                    texts = item['translations'][language]
                    self.assertTrue(texts['name'] and texts['description'])
