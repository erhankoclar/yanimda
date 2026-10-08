"""
care modellerinin manager'ları.

Manager'lar yalnızca queryset döndüren metotlar içerir; iş akışları ve
hesaplamalar `apps.care.services` altındaki servislerdedir. Servisler
modellere bu manager'lar üzerinden erişir.
"""

from django.db import models
from django.db.models import Count
from parler.managers import TranslatableManager, TranslatableQuerySet


class ServiceTypeQuerySet(TranslatableQuerySet):
    def active(self):
        """
        Yayında olan hizmet türlerini gösterim sırasıyla, çevirileri önceden yüklenmiş döndürür.

        Returns:
            ServiceTypeQuerySet: Aktif hizmet türleri.
        """
        return self.filter(is_active=True).prefetch_related('translations').order_by('sort_order', 'slug')

    def with_demand(self):
        """
        Her hizmete başvuru ve hızlı talep toplamını `demand` olarak ekler.

        Returns:
            ServiceTypeQuerySet: `demand` ile işaretlenmiş hizmetler.
        """
        return self.annotate(demand=Count('requests', distinct=True) + Count('inquiries', distinct=True))


class CreatedAtQuerySet(models.QuerySet):
    """Oluşturulma zamanına göre ortak filtreler."""

    def created_on_or_after(self, day):
        """
        Belirtilen günden (yerel saat) itibaren oluşturulan kayıtları döndürür.

        Args:
            day (date): İlk gün.

        Returns:
            QuerySet: Filtrelenmiş kayıtlar.
        """
        return self.filter(created_at__date__gte=day)

    def latest_first(self):
        """
        Kayıtları hizmetiyle birlikte en yeniden eskiye döndürür.

        Returns:
            QuerySet: Sıralı kayıtlar.
        """
        return self.select_related('service', 'neighborhood__district').prefetch_related('service__translations').order_by('-created_at')


class CareRequestQuerySet(CreatedAtQuerySet):
    def open(self):
        """
        Henüz kapanmamış (yeni, inceleniyor, atandı) başvuruları döndürür.

        Returns:
            CareRequestQuerySet: Açık başvurular.
        """
        return self.filter(status__in=self.model.OPEN_STATUSES)

    def waiting_for_review(self):
        """
        Ekibin ilgilenmesini bekleyen (yeni, inceleniyor) başvuruları en eskiden yeniye döndürür.

        Returns:
            CareRequestQuerySet: Bekleyen başvurular.
        """
        statuses = [self.model.Status.NEW, self.model.Status.REVIEWING]
        return self.filter(status__in=statuses).select_related('service', 'neighborhood__district').prefetch_related('service__translations').order_by('created_at')


class ServiceInquiryQuerySet(CreatedAtQuerySet):
    pass


ServiceTypeManager = TranslatableManager.from_queryset(ServiceTypeQuerySet)
CareRequestManager = models.Manager.from_queryset(CareRequestQuerySet)
ServiceInquiryManager = models.Manager.from_queryset(ServiceInquiryQuerySet)
