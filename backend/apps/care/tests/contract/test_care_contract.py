from django.core.cache import cache
from django.urls import reverse
from rest_framework.test import APITestCase

from apps.care.models import CareRequest
from apps.care.tests.factories import make_care_request, make_service, make_user

REQUEST_FIELDS = {
    'id', 'service_detail', 'elder_full_name', 'elder_age', 'relationship', 'elder_notes',
    'preferred_date', 'time_slot', 'location', 'address', 'contact_phone',
    'alternate_contact_name', 'alternate_contact_phone', 'status', 'status_display', 'created_at',
}


class CareResponseContractTests(APITestCase):
    """Frontend sihirbazı ve talep ekranlarının bağlı olduğu yanıt şekillerini sabitler."""

    def setUp(self):
        """Throttle sayaçlarını sıfırlar ve oturum açmış kullanıcı hazırlar."""
        cache.clear()
        self.user = make_user()
        self.client.force_authenticate(self.user)

    def test_service_list_is_plain_array_of_cards(self):
        """
        Hizmet listesinin sayfalanmamış dizi ve sabit kart alanlarıyla döndüğünü doğrular.

        Senaryo:
        - Bir hizmet oluşturulur ve liste çağrılır.

        Beklenti:
        - Yanıt dizi olmalı; her öğe {id, name, slug, description, icon} alanlarına sahip olmalıdır.
        """
        make_service()

        data = self.client.get(reverse('care:service-list')).data

        self.assertIsInstance(data, list)
        self.assertEqual(set(data[0]), {'id', 'name', 'slug', 'description', 'icon'})

    def test_request_list_is_paginated_with_fixed_fields(self):
        """
        Talep listesinin sayfalı zarf ve sabit talep alanlarıyla döndüğünü doğrular.

        Senaryo:
        - Kullanıcıya ait bir talep oluşturulur ve liste çağrılır.

        Beklenti:
        - Zarf {count, next, previous, results} olmalı; talep alanları sabit kümeyle eşleşmelidir.
        """
        make_care_request(applicant=self.user)

        data = self.client.get(reverse('care:request-list')).data

        self.assertEqual(set(data), {'count', 'next', 'previous', 'results'})
        self.assertEqual(set(data['results'][0]), REQUEST_FIELDS)

    def test_request_detail_value_formats(self):
        """
        Talep detayındaki değer biçimlerini doğrular.

        Senaryo:
        - Talep detayı çağrılır.

        Beklenti:
        - Tarih ISO `YYYY-MM-DD`, durum ve seçenekler model değerleri, hizmet detayı kart alanları olmalıdır.
        """
        care_request = make_care_request(applicant=self.user)

        data = self.client.get(reverse('care:request-detail', args=[care_request.pk])).data

        self.assertEqual(set(data), REQUEST_FIELDS)
        self.assertEqual(data['preferred_date'], care_request.preferred_date.isoformat())
        self.assertIn(data['status'], CareRequest.Status.values)
        self.assertIn(data['time_slot'], CareRequest.TimeSlot.values)
        self.assertIn(data['relationship'], CareRequest.Relationship.values)
        self.assertEqual(set(data['service_detail']), {'id', 'name', 'slug', 'description', 'icon'})
