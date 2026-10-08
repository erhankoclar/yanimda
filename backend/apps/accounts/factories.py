"""Kullanıcı hesapları için factory-boy fabrikaları; testler ve demo verisi kullanır."""

import factory
from django.conf import settings
from django.contrib.auth import get_user_model


class UserFactory(factory.django.DjangoModelFactory):
    """
    Benzersiz, küçük harfli e-postalı başvuru sahibi hesabı üretir.

    Parola `TEST_USER_PASSWORD` ayarından kayıt anında okunur ve `factory.django.Password`
    ile özetlenerek yazılır; üretilen hesapla giriş yapılabilir.
    """

    class Meta:
        model = get_user_model()

    email = factory.Sequence(lambda number: f'kullanici{number}@example.com')
    password = factory.django.Password(factory.LazyFunction(lambda: settings.TEST_USER_PASSWORD))
    first_name = factory.Faker('first_name', locale='tr_TR')
    last_name = factory.Faker('last_name', locale='tr_TR')
