"""Senaryo testlerinin ortak altyapısı: gerçek kayıt/giriş akışıyla çalışan aktörler."""

from datetime import timedelta

from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.utils import timezone
from rest_framework.test import APIClient, APITestCase

from apps.care.models import ServiceType

PASSWORD = 'Yanimda-Guclu-2026'


class Actor:
    """Kendi API istemcisi ve JWT oturumu olan bir kullanıcıyı temsil eder."""

    def __init__(self, email, password=PASSWORD):
        """
        Aktörü oturumsuz bir API istemcisiyle hazırlar.

        Args:
            email (str): Aktörün e-posta adresi.
            password (str): Aktörün parolası.
        """
        self.email = email
        self.password = password
        self.client = APIClient()
        self.refresh = None

    def register(self, **overrides):
        """
        Kayıt endpoint'iyle hesap açar.

        Args:
            **overrides (Any): Kayıt alanlarını ezen değerler.

        Returns:
            Response: Kayıt yanıtı.
        """
        payload = {'email': self.email, 'password': self.password, 'first_name': 'Ayşe', 'last_name': 'Yılmaz'}
        return self.client.post('/api/auth/register/', {**payload, **overrides}, format='json')

    def login(self, email=None, password=None):
        """
        Token endpoint'iyle giriş yapar; başarılıysa istemciye Bearer başlığı ekler.

        Args:
            email (Optional[str]): Girişte yazılan e-posta; verilmezse aktörün e-postası.
            password (Optional[str]): Girişte yazılan parola; verilmezse aktörün parolası.

        Returns:
            Response: Giriş yanıtı.
        """
        response = self.client.post('/api/auth/token/', {
            'email': email or self.email, 'password': password or self.password,
        }, format='json')
        if response.status_code == 200:
            self.refresh = response.data['refresh']
            self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {response.data['access']}")
        return response

    def apply(self, service, **overrides):
        """
        Geçerli verilerle hizmet başvurusu yapar.

        Args:
            service (ServiceType): Başvurulan hizmet.
            **overrides (Any): Başvuru alanlarını ezen değerler.

        Returns:
            Response: Başvuru yanıtı.
        """
        payload = {
            'service': service.id, 'elder_full_name': 'Fatma Yılmaz', 'elder_age': 78, 'relationship': 'parent',
            'preferred_date': (timezone.localdate() + timedelta(days=3)).isoformat(), 'time_slot': 'morning',
            'city': 'Samsun', 'district': 'İlkadım', 'address': 'Örnek Mah. No: 1',
            'contact_phone': '05551112233', 'consent': True,
        }
        return self.client.post('/api/requests/', {**payload, **overrides}, format='json')

    def get(self, path, params=None):
        """
        Aktörün oturumuyla GET isteği yapar.

        Args:
            path (str): İstek yolu.
            params (Optional[dict[str, Any]]): Sorgu parametreleri.

        Returns:
            Response: Yanıt.
        """
        return self.client.get(path, params or {})

    def patch(self, path, data):
        """
        Aktörün oturumuyla JSON PATCH isteği yapar.

        Args:
            path (str): İstek yolu.
            data (dict[str, Any]): Gövde.

        Returns:
            Response: Yanıt.
        """
        return self.client.patch(path, data, format='json')


class ScenarioTestCase(APITestCase):
    """Hizmet kataloğu ve admin aktörü hazır senaryo test sınıfı."""

    def setUp(self):
        """Throttle sayaçlarını sıfırlar, iki hizmet ve oturum açmış bir admin hazırlar."""
        cache.clear()
        self.companion = ServiceType.objects.create(
            name='Refakat', slug='refakat', description='-', icon='companion', sort_order=1,
        )
        self.hospital = ServiceType.objects.create(
            name='Hastane eşliği', slug='hastane', description='-', icon='hospital', sort_order=2,
        )
        get_user_model().objects.create_user(email='admin@yanimda.example', password=PASSWORD, is_staff=True)
        self.admin = Actor('admin@yanimda.example')
        self.admin.login()

    def new_applicant(self, email='ayse@example.com'):
        """
        Kayıt olup giriş yapmış yeni bir başvuru sahibi döndürür.

        Args:
            email (str): Başvuru sahibinin e-postası.

        Returns:
            Actor: Oturum açmış başvuru sahibi.
        """
        actor = Actor(email)
        actor.register()
        actor.login()
        return actor
