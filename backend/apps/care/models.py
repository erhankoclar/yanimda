from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
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

    class Meta:
        verbose_name = _('care request')
        verbose_name_plural = _('care requests')
        ordering = ['-created_at']

    STATUS_TRANSITIONS = {
        Status.NEW: [Status.REVIEWING, Status.CANCELLED],
        Status.REVIEWING: [Status.ASSIGNED, Status.CANCELLED],
        Status.ASSIGNED: [Status.COMPLETED, Status.CANCELLED],
        Status.COMPLETED: [],
        Status.CANCELLED: [],
    }

    def next_statuses(self):
        """
        Talebin mevcut durumundan geçilebilecek durumları döndürür.

        Returns:
            list[str]: Geçişe izin verilen durum değerleri; son durumlarda boş liste.
        """
        return list(self.STATUS_TRANSITIONS[self.status])

    def can_change_status_to(self, new_status):
        """
        Mevcut durumdan verilen duruma geçilip geçilemeyeceğini söyler.

        Aynı duruma "geçiş" her zaman serbesttir; böylece yalnızca not güncellenebilir.

        Args:
            new_status (str): Hedef durum değeri.

        Returns:
            bool: Geçişe izin veriliyorsa True.
        """
        return new_status == self.status or new_status in self.STATUS_TRANSITIONS[self.status]

    def __str__(self):
        """
        Talebin hizmet ve yaşlı adıyla okunabilir temsilini döndürür.

        Returns:
            str: `#<id> <hizmet> - <yaşlı adı>` biçiminde metin.
        """
        return f'#{self.pk} {self.service} - {self.elder_full_name}'
