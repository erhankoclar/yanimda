"""Bakım modülü için factory-boy fabrikaları; testler ve demo verisi kullanır."""

from datetime import timedelta

import factory
from django.conf import settings
from django.utils import timezone

from apps.accounts.factories import UserFactory
from apps.care.models import CareRequest, ServiceInquiry, ServiceType

# Faker'ın tr_TR adres sağlayıcısı İngilizce şehir adlarına düştüğü için şehirler buradan seçilir.
CITIES = ['İstanbul', 'Ankara', 'İzmir', 'Bursa', 'Samsun', 'Antalya', 'Eskişehir', 'Trabzon']


class BackdatedFactory(factory.django.DjangoModelFactory):
    """
    `created_at` verilebilen fabrikaların ortak tabanı.

    Modellerdeki `auto_now_add` alanı kayıtta şimdiki zamanı yazdığından, verilen
    tarih kayıttan sonra tek bir güncelleme sorgusuyla uygulanır.
    """

    class Meta:
        abstract = True

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        """
        Kaydı oluşturur; `created_at` verildiyse kayıttan sonra onu yazar.

        Args:
            model_class (type[Model]): Oluşturulacak model.
            *args (Any): Model yapıcısına aktarılan konumsal argümanlar.
            **kwargs (Any): Model alanları; isteğe bağlı `created_at`.

        Returns:
            Model: Oluşturulan kayıt.
        """
        created_at = kwargs.pop('created_at', None)
        instance = super()._create(model_class, *args, **kwargs)
        if created_at is not None:
            model_class.objects.filter(pk=instance.pk).update(created_at=created_at)
            instance.created_at = created_at
        return instance


class ServiceTypeFactory(factory.django.DjangoModelFactory):
    """
    Benzersiz slug'lı aktif hizmet türü üretir.

    Ad ve açıklama, o an etkin dilden bağımsız olarak varsayılan dilin (Türkçe) çevirisine yazılır;
    başka dil satırı gerekiyorsa `set_current_language` ile ayrıca eklenir.
    """

    class Meta:
        model = ServiceType

    _current_language = factory.LazyFunction(lambda: settings.PARLER_DEFAULT_LANGUAGE_CODE)

    name = factory.Sequence(lambda number: f'Hizmet {number}')
    slug = factory.Sequence(lambda number: f'hizmet-{number}')
    description = 'Açıklama'
    icon = 'companion'
    sort_order = factory.Sequence(lambda number: number)


class ServiceInquiryFactory(BackdatedFactory):
    """Kurgusal kişiden gelen hızlı talep üretir."""

    class Meta:
        model = ServiceInquiry

    class Params:
        # Faker'ın tr_TR `name` sağlayıcısı unvan ve dört parçalı ad üretebildiği için ad ve soyad ayrı üretilir.
        first_name = factory.Faker('first_name', locale='tr_TR')
        last_name = factory.Faker('last_name', locale='tr_TR')

    full_name = factory.LazyAttribute(lambda inquiry: f'{inquiry.first_name} {inquiry.last_name}')
    email = factory.Sequence(lambda number: f'talep{number}@example.com')
    service = factory.SubFactory(ServiceTypeFactory)
    message = factory.Faker('random_element', elements=[
        'Haftada iki gün birkaç saatlik destek arıyoruz.',
        'Annem için kısa süreli yardım gerekiyor, ayrıntıları konuşmak isteriz.',
        'Babamın hastane randevularına eşlik edecek biri lazım.',
        'Pazar alışverişi ve eczane işleri için yardım istiyoruz.',
    ])
    consent_given_at = factory.LazyFunction(timezone.now)


class CareRequestFactory(BackdatedFactory):
    """Geçerli alanlarla dolu hizmet başvurusu üretir."""

    class Meta:
        model = CareRequest

    applicant = factory.SubFactory(UserFactory)
    service = factory.SubFactory(ServiceTypeFactory)
    class Params:
        # Unvansız, iki parçalı yaşlı adı için ad ve soyad ayrı üretilir.
        elder_first_name = factory.Faker('first_name', locale='tr_TR')
        elder_last_name = factory.Faker('last_name', locale='tr_TR')

    elder_full_name = factory.LazyAttribute(lambda request: f'{request.elder_first_name} {request.elder_last_name}')
    elder_age = factory.Faker('random_int', min=62, max=94)
    relationship = factory.Faker('random_element', elements=CareRequest.Relationship.values)
    elder_notes = ''
    preferred_date = factory.LazyFunction(lambda: timezone.localdate() + timedelta(days=3))
    time_slot = factory.Faker('random_element', elements=CareRequest.TimeSlot.values)
    city = factory.Faker('random_element', elements=CITIES)
    district = 'Merkez'
    address = factory.Sequence(lambda number: f'Kurgu Sok. No: {number}')
    contact_phone = '05550000000'
    consent_given_at = factory.LazyFunction(timezone.now)
