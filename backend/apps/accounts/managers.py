from django.contrib.auth.base_user import BaseUserManager
from django.utils.translation import gettext


class UserManager(BaseUserManager):
    """E-posta adresini kullanıcı adı olarak kullanan kullanıcı yöneticisi."""

    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        """
        Verilen e-posta ve parola ile kullanıcıyı oluşturup kaydeder.

        Args:
            email (str): Kullanıcının giriş için kullanacağı e-posta adresi.
            password (Optional[str]): Ham parola; None ise kullanılamaz parola atanır.
            **extra_fields (Any): Modele aktarılacak ek alanlar.

        Returns:
            User: Oluşturulan kullanıcı.

        Raises:
            ValueError: E-posta adresi boş olduğunda.
        """
        if not email:
            raise ValueError(gettext('The email address is required.'))
        email = self.normalize_email(email).lower()
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        """
        Yönetici yetkisi olmayan standart bir kullanıcı oluşturur.

        Args:
            email (str): Kullanıcının e-posta adresi.
            password (Optional[str]): Ham parola.
            **extra_fields (Any): Modele aktarılacak ek alanlar.

        Returns:
            User: Oluşturulan kullanıcı.

        Raises:
            ValueError: E-posta adresi boş olduğunda.
        """
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password=None, **extra_fields):
        """
        Admin paneline ve Django yönetimine tam erişimi olan kullanıcı oluşturur.

        Args:
            email (str): Kullanıcının e-posta adresi.
            password (Optional[str]): Ham parola.
            **extra_fields (Any): Modele aktarılacak ek alanlar.

        Returns:
            User: Oluşturulan süper kullanıcı.

        Raises:
            ValueError: E-posta boşsa ya da is_staff/is_superuser False verilmişse.
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        if extra_fields.get('is_staff') is not True:
            raise ValueError(gettext('Superuser must have is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(gettext('Superuser must have is_superuser=True.'))
        return self._create_user(email, password, **extra_fields)
