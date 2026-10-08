"""
geo modellerinin manager'ları.

Manager'lar yalnızca queryset döndüren metotlar içerir; veri yükleme ve okuma
akışları `apps.geo.services` altındaki servislerdedir.
"""

from django.db import models


class DistrictQuerySet(models.QuerySet):
    def ordered(self):
        """
        İlçeleri Türkçe alfabe sırasıyla döndürür.

        Returns:
            DistrictQuerySet: Sıralı ilçeler.
        """
        return self.order_by('sort_order', 'id')


class NeighborhoodQuerySet(models.QuerySet):
    def active(self):
        """
        Başvuru ve hızlı talep formlarında seçilebilen mahalleleri döndürür.

        Şu an tüm mahalleler seçilebilir; ileride hizmet dışı bırakılan mahalleler burada süzülür.

        Returns:
            NeighborhoodQuerySet: Seçilebilir mahalleler.
        """
        return self.all()

    def in_district(self, district_id):
        """
        Bir ilçenin mahallelerini Türkçe alfabe sırasıyla döndürür.

        Args:
            district_id (int): İlçe kimliği.

        Returns:
            NeighborhoodQuerySet: Sıralı mahalleler.
        """
        return self.filter(district_id=district_id).order_by('sort_order', 'id')


DistrictManager = models.Manager.from_queryset(DistrictQuerySet)
NeighborhoodManager = models.Manager.from_queryset(NeighborhoodQuerySet)
