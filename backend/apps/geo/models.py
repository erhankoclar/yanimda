from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.geo.managers import DistrictManager, NeighborhoodManager


class District(models.Model):
    """
    Hizmet verilen ilin (İstanbul) ilçesi.

    Sınırlar OpenStreetMap'ten gelir; `osm_id` haritadaki poligonla eşleşmeyi sağlar.
    Adlar özel ad olduğu için çevrilmez.
    """

    osm_id = models.BigIntegerField(_('OpenStreetMap id'), unique=True)
    name = models.CharField(_('name'), max_length=100)
    slug = models.SlugField(_('slug'), max_length=100, unique=True)
    sort_order = models.PositiveSmallIntegerField(_('sort order'), default=0)

    objects = DistrictManager()

    class Meta:
        verbose_name = _('district')
        verbose_name_plural = _('districts')
        ordering = ['sort_order', 'id']

    def __str__(self):
        """
        İlçenin adını döndürür.

        Returns:
            str: İlçe adı.
        """
        return self.name


class Neighborhood(models.Model):
    """Bir ilçeye bağlı mahalle; başvuru ve hızlı taleplerin konumu bu düzeyde tutulur."""

    osm_id = models.BigIntegerField(_('OpenStreetMap id'), unique=True)
    district = models.ForeignKey(
        District, on_delete=models.PROTECT, related_name='neighborhoods', verbose_name=_('district'),
    )
    name = models.CharField(_('name'), max_length=150)
    sort_order = models.PositiveSmallIntegerField(_('sort order'), default=0)

    objects = NeighborhoodManager()

    class Meta:
        verbose_name = _('neighborhood')
        verbose_name_plural = _('neighborhoods')
        ordering = ['sort_order', 'id']

    def __str__(self):
        """
        Mahallenin adını döndürür.

        Returns:
            str: Mahalle adı.
        """
        return self.name
