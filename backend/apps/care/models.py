from django.db import models
from django.utils.translation import gettext_lazy as _


class ServiceType(models.Model):
    """
    Başvuru sihirbazının ilk adımında seçilen hizmet türü.

    `icon` alanı frontend'deki ikon eşlemesinin anahtarıdır; ikon dosyası değildir.
    """

    name = models.CharField(_('name'), max_length=100)
    slug = models.SlugField(_('slug'), max_length=100, unique=True)
    description = models.CharField(_('description'), max_length=255)
    icon = models.CharField(_('icon key'), max_length=50)
    sort_order = models.PositiveSmallIntegerField(_('sort order'), default=0)
    is_active = models.BooleanField(_('active'), default=True)

    class Meta:
        verbose_name = _('service type')
        verbose_name_plural = _('service types')
        ordering = ['sort_order', 'name']

    def __str__(self):
        """
        Hizmet türünün adını döndürür.

        Returns:
            str: Hizmet adı.
        """
        return self.name
