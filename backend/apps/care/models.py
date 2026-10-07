from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.care.managers import CareRequestManager, ServiceInquiryManager, ServiceTypeManager
from apps.care.text import person_name_key


class ServiceType(models.Model):
    """
    Başvuru sihirbazının ilk adımında seçilen hizmet türü.

    `icon` alanı frontend'deki ikon eşlemesinin anahtarıdır; ikon dosyası değildir.
    """

    name = models.CharField(_('name'), max_length=100)
    slug = models.SlugField(_('slug'), max_length=100, unique=True)
    description = models.CharField(_('description'), max_length=255)
    # İngilizce arayüz için karşılıklar; boşsa Türkçe metin gösterilir.
    name_en = models.CharField(_('name (English)'), max_length=100, blank=True)
    description_en = models.CharField(_('description (English)'), max_length=255, blank=True)
    icon = models.CharField(_('icon key'), max_length=50)
    sort_order = models.PositiveSmallIntegerField(_('sort order'), default=0)
    is_active = models.BooleanField(_('active'), default=True)

    objects = ServiceTypeManager()

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


class CareRequest(models.Model):
    """
    Bir yakının yaşlısı adına yaptığı hizmet başvurusu.

    Başvuru sahibi yalnızca kendi taleplerini görür; durum ve admin notu
    yalnızca admin panelinden değiştirilir.
    """

    class Status(models.TextChoices):
        NEW = 'new', _('New')
        REVIEWING = 'reviewing', _('Reviewing')
        ASSIGNED = 'assigned', _('Assigned')
        COMPLETED = 'completed', _('Completed')
        CANCELLED = 'cancelled', _('Cancelled')

    class Relationship(models.TextChoices):
        PARENT = 'parent', _('Mother / father')
        GRANDPARENT = 'grandparent', _('Grandparent')
        RELATIVE = 'relative', _('Other relative')
        NEIGHBOR = 'neighbor', _('Neighbor / friend')
        SELF = 'self', _('Myself')

    class TimeSlot(models.TextChoices):
        MORNING = 'morning', _('Morning (08:00-12:00)')
        AFTERNOON = 'afternoon', _('Afternoon (12:00-17:00)')
        EVENING = 'evening', _('Evening (17:00-21:00)')

    applicant = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='care_requests',
        verbose_name=_('applicant'),
    )
    service = models.ForeignKey(
        ServiceType, on_delete=models.PROTECT, related_name='requests', verbose_name=_('service'),
    )
    elder_full_name = models.CharField(_('elder full name'), max_length=150)
    # Mükerrer talep kontrolü için Türkçe harf ve büyük/küçük harf duyarsız ad anahtarı.
    elder_name_key = models.CharField(_('elder name key'), max_length=150, default='', editable=False)
    elder_age = models.PositiveSmallIntegerField(
        _('elder age'), validators=[MinValueValidator(40), MaxValueValidator(120)],
    )
    relationship = models.CharField(_('relationship'), max_length=20, choices=Relationship.choices)
    elder_notes = models.TextField(_('special notes'), blank=True)
    preferred_date = models.DateField(_('preferred date'))
    time_slot = models.CharField(_('time slot'), max_length=20, choices=TimeSlot.choices)
    city = models.CharField(_('city'), max_length=50)
    district = models.CharField(_('district'), max_length=50)
    address = models.TextField(_('address'))
    contact_phone = models.CharField(_('contact phone'), max_length=20)
    alternate_contact_name = models.CharField(_('alternate contact name'), max_length=150, blank=True)
    alternate_contact_phone = models.CharField(_('alternate contact phone'), max_length=20, blank=True)
    consent_given_at = models.DateTimeField(_('consent given at'))
    status = models.CharField(_('status'), max_length=20, choices=Status.choices, default=Status.NEW, db_index=True)
    admin_note = models.TextField(_('admin note'), blank=True)
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)

    OPEN_STATUSES = [Status.NEW, Status.REVIEWING, Status.ASSIGNED]

    objects = CareRequestManager()

    class Meta:
        verbose_name = _('care request')
        verbose_name_plural = _('care requests')
        ordering = ['-created_at']
        constraints = [
            # Aynı başvuru sahibi, aynı yaşlı için aynı hizmete birden fazla açık talep tutamaz.
            models.UniqueConstraint(
                fields=['applicant', 'service', 'elder_name_key'],
                condition=models.Q(status__in=['new', 'reviewing', 'assigned']),
                name='care_request_unique_open_per_elder_service',
            ),
        ]

    STATUS_TRANSITIONS = {
        Status.NEW: [Status.REVIEWING, Status.CANCELLED],
        Status.REVIEWING: [Status.ASSIGNED, Status.CANCELLED],
        Status.ASSIGNED: [Status.COMPLETED, Status.CANCELLED],
        Status.COMPLETED: [],
        Status.CANCELLED: [],
    }

    def save(self, *args, **kwargs):
        """
        Kaydetmeden önce yaşlı adının karşılaştırma anahtarını günceller.

        Args:
            *args (Any): Model.save konumsal argümanları.
            **kwargs (Any): Model.save isimli argümanları.
        """
        self.elder_name_key = person_name_key(self.elder_full_name)
        update_fields = kwargs.get('update_fields')
        if update_fields is not None and 'elder_full_name' in update_fields:
            kwargs['update_fields'] = {*update_fields, 'elder_name_key'}
        super().save(*args, **kwargs)

    def __str__(self):
        """
        Talebin hizmet ve yaşlı adıyla okunabilir temsilini döndürür.

        Returns:
            str: `#<id> <hizmet> - <yaşlı adı>` biçiminde metin.
        """
        return f'#{self.pk} {self.service} - {self.elder_full_name}'


class ServiceInquiry(models.Model):
    """
    Hesap açmadan ana sayfadaki hızlı formla bırakılan hizmet talebi.

    Ekip bu talepleri inceleyip kişiyi e-posta veya telefonla arar; ayrıntılı
    başvuru (CareRequest) gerekirse görüşme sonrasında oluşturulur.
    """

    full_name = models.CharField(_('full name'), max_length=150)
    email = models.EmailField(_('email address'))
    service = models.ForeignKey(
        ServiceType, on_delete=models.PROTECT, related_name='inquiries', verbose_name=_('service'),
    )
    message = models.TextField(_('description'))
    consent_given_at = models.DateTimeField(_('consent given at'))
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)

    objects = ServiceInquiryManager()

    class Meta:
        verbose_name = _('service inquiry')
        verbose_name_plural = _('service inquiries')
        ordering = ['-created_at']

    def __str__(self):
        """
        Talebin numara, kişi ve hizmetle okunabilir temsilini döndürür.

        Returns:
            str: `#<id> <ad soyad> - <hizmet>` biçiminde metin.
        """
        return f'#{self.pk} {self.full_name} - {self.service}'
