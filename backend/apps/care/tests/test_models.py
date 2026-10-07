from django.db import IntegrityError
from django.test import TestCase

from apps.care.models import ServiceType


class ServiceTypeModelTests(TestCase):
    def test_default_ordering_uses_sort_order(self):
        """
        Hizmet türlerinin sıra numarasına göre listelendiğini doğrular.

        Senaryo:
        - Sıra numarası ters olan iki hizmet oluşturulur.

        Beklenti:
        - Küçük sıra numaralı hizmet önce gelmelidir.
        """
        ServiceType.objects.create(name='B', slug='b', description='-', icon='x', sort_order=20)
        ServiceType.objects.create(name='A', slug='a', description='-', icon='x', sort_order=10)

        self.assertEqual(list(ServiceType.objects.values_list('slug', flat=True)), ['a', 'b'])

    def test_slug_is_unique(self):
        """Aynı slug ile ikinci hizmet türü oluşturulamadığını doğrular (hata yolu)."""
        ServiceType.objects.create(name='A', slug='a', description='-', icon='x')

        with self.assertRaises(IntegrityError):
            ServiceType.objects.create(name='A2', slug='a', description='-', icon='x')

    def test_str_returns_name(self):
        """Metin temsilinin hizmet adı olduğunu doğrular."""
        service = ServiceType(name='Refakat', slug='refakat', description='-', icon='companion')

        self.assertEqual(str(service), 'Refakat')
