"""
Kullanıcı manager'ı.

Manager yalnızca queryset döndüren metotlar içerir; hesap oluşturma gibi iş
akışları `apps.accounts.services.user_service` içindedir. Django'nun
`createsuperuser` komutu ve kimlik doğrulama arka ucu `create_user`,
`create_superuser` ve `get_by_natural_key` kancalarını manager'da aradığı için
bu kancalar yalnızca servise yönlendirme yapar.
"""

from django.contrib.auth.base_user import BaseUserManager
from django.db import models
from django.db.models import Count


class UserQuerySet(models.QuerySet):
    def with_request_count(self):
        """
        Her kullanıcıya oluşturduğu başvuru sayısını `request_count` olarak ekler.

        Returns:
            UserQuerySet: İşaretlenmiş kullanıcılar.
        """
        return self.annotate(request_count=Count('care_requests'))

    def by_email(self, email):
        """
        E-postası büyük/küçük harf ve baş/son boşluklardan bağımsız eşleşen kullanıcıları döndürür.

        Args:
            email (str): Aranan e-posta.

        Returns:
            UserQuerySet: Eşleşen kullanıcılar (en fazla bir kayıt).
        """
        return self.filter(email__iexact=email.strip())


class UserManager(BaseUserManager.from_queryset(UserQuerySet)):
    """E-posta adresini kullanıcı adı olarak kullanan kullanıcı manager'ı."""

    use_in_migrations = True

    def get_by_natural_key(self, username):
        """
        Kimlik doğrulama arka ucu için kullanıcıyı e-postasıyla bulur (Django kancası).

        Args:
            username (str): Girişte yazılan e-posta adresi.

        Returns:
            User: Eşleşen kullanıcı.

        Raises:
            User.DoesNotExist: E-postaya ait kullanıcı yoksa.
        """
        return self.by_email(username).get()

    def create_user(self, email, password=None, **extra_fields):
        """
        Django kancası; kullanıcı oluşturmayı servise yönlendirir.

        Args:
            email (str): Giriş e-postası.
            password (Optional[str]): Ham parola.
            **extra_fields (Any): Ek alanlar.

        Returns:
            User: Oluşturulan kullanıcı.

        Raises:
            ValueError: E-posta adresi boş olduğunda.
        """
        from apps.accounts.services import user_service

        return user_service.create_user(email, password, **extra_fields)

    def create_superuser(self, email, password=None, **extra_fields):
        """
        Django kancası (`createsuperuser`); süper kullanıcı oluşturmayı servise yönlendirir.

        Args:
            email (str): Giriş e-postası.
            password (Optional[str]): Ham parola.
            **extra_fields (Any): Ek alanlar.

        Returns:
            User: Oluşturulan süper kullanıcı.

        Raises:
            ValueError: E-posta boşsa ya da yetki bayrakları False verilmişse.
        """
        from apps.accounts.services import user_service

        return user_service.create_superuser(email, password, **extra_fields)
