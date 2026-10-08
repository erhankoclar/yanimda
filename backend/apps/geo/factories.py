"""İlçe ve mahalle için factory-boy fabrikaları; testler kullanır."""

import factory

from apps.geo.models import District, Neighborhood


class DistrictFactory(factory.django.DjangoModelFactory):
    """Benzersiz OSM kimlikli ve slug'lı ilçe üretir."""

    class Meta:
        model = District

    osm_id = factory.Sequence(lambda number: 900000000 + number)
    name = factory.Sequence(lambda number: f'İlçe {number}')
    slug = factory.Sequence(lambda number: f'ilce-{number}')
    sort_order = factory.Sequence(lambda number: number % 1000)


class NeighborhoodFactory(factory.django.DjangoModelFactory):
    """Bir ilçeye bağlı, benzersiz OSM kimlikli mahalle üretir."""

    class Meta:
        model = Neighborhood

    osm_id = factory.Sequence(lambda number: 950000000 + number)
    district = factory.SubFactory(DistrictFactory)
    name = factory.Sequence(lambda number: f'Deneme {number} Mahallesi')
    sort_order = factory.Sequence(lambda number: number % 1000)
