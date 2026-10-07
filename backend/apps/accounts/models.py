from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _

from .managers import UserManager


class User(AbstractUser):
    """
    E-posta ile giriş yapan Yanımda kullanıcısı.

    Başvuru yapan yakınlar standart kullanıcıdır; `is_staff` olan kullanıcılar
    admin paneline erişebilir.
    """

    username = None
    email = models.EmailField(_('email address'), unique=True)
    phone = models.CharField(_('phone'), max_length=20, blank=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')
        ordering = ['-date_joined']

    def __str__(self):
        """
        Kullanıcının okunabilir temsilini döndürür.

        Returns:
            str: Ad soyad varsa ad soyad, yoksa e-posta adresi.
        """
        return self.get_full_name() or self.email
