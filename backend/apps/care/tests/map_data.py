"""Tematik harita testlerinin ortak küçük veri kümesini kuran yardımcı."""

from datetime import timedelta
from types import SimpleNamespace

from django.utils import timezone

from apps.care.factories import CareRequestFactory, ServiceInquiryFactory, ServiceTypeFactory
from apps.geo.factories import DistrictFactory, NeighborhoodFactory


def build_dataset():
    """
    İki hizmet, üç ilçe ve dört mahalleden oluşan küçük bir harita veri kümesi kurar.

    Dağılım: n1 = 2 hızlı talep + 1 başvuru (s1); n2 = 1 başvuru (s2); n3 = 1 hızlı talep (s2);
    n4 hiç kayıt almaz; ayrıca mahallesiz bir hızlı talep vardır.

    Returns:
        SimpleNamespace: `s1`, `s2`, `d1`, `d2`, `d3`, `n1`..`n4` nesneleri.
    """
    s1 = ServiceTypeFactory(name='Refakat', sort_order=1)
    s2 = ServiceTypeFactory(name='Küçük tamir', sort_order=2)
    d1, d2, d3 = DistrictFactory(sort_order=1), DistrictFactory(sort_order=2), DistrictFactory(sort_order=3)
    n1, n2 = NeighborhoodFactory(district=d1), NeighborhoodFactory(district=d1)
    n3, n4 = NeighborhoodFactory(district=d2), NeighborhoodFactory(district=d3)
    ServiceInquiryFactory.create_batch(2, service=s1, neighborhood=n1)
    CareRequestFactory(service=s1, neighborhood=n1)
    CareRequestFactory(service=s2, neighborhood=n2)
    ServiceInquiryFactory(service=s2, neighborhood=n3)
    ServiceInquiryFactory(service=s1, neighborhood=None)
    return SimpleNamespace(s1=s1, s2=s2, d1=d1, d2=d2, d3=d3, n1=n1, n2=n2, n3=n3, n4=n4)


def days_ago(days):
    """
    Şimdiden verilen gün kadar önceki zamanı döndürür.

    Args:
        days (int): Geriye gidilecek gün sayısı.

    Returns:
        datetime: Zaman damgası.
    """
    return timezone.now() - timedelta(days=days)
