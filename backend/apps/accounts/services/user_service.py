"""Kullanıcı hesapları için iş akışları ve okuma servisleri."""

from django.contrib.auth import get_user_model
from django.contrib.auth.base_user import BaseUserManager
from django.utils.translation import gettext

# Profil güncellemesinde değiştirilebilen alanlar; e-posta ve yetkiler buraya girmez.
PROFILE_FIELDS = ('first_name', 'last_name', 'phone')


def create_user(email, password=None, **extra_fields):
    """
    E-postası normalleştirilmiş, parolası özetlenmiş kullanıcıyı oluşturup kaydeder.

    Args:
        email (str): Giriş e-posta adresi.
        password (Optional[str]): Ham parola; None ise kullanılamaz parola atanır.
        **extra_fields (Any): Modele aktarılacak ek alanlar (ör. ad, telefon, yetki bayrakları).

    Returns:
        User: Oluşturulan kullanıcı.

    Raises:
        ValueError: E-posta adresi boş olduğunda.
    """
    if not email:
        raise ValueError(gettext('The email address is required.'))
    extra_fields.setdefault('is_staff', False)
    extra_fields.setdefault('is_superuser', False)
    user = get_user_model()(email=BaseUserManager.normalize_email(email).lower(), **extra_fields)
    user.set_password(password)
    user.save()
    return user


def create_superuser(email, password=None, **extra_fields):
    """
    Admin paneline tam erişimi olan kullanıcı oluşturur.

    Args:
        email (str): Giriş e-posta adresi.
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
    return create_user(email, password, **extra_fields)


def register_applicant(*, email, password, first_name, last_name, phone=''):
    """
    Kayıt formundan admin yetkisi olmayan başvuru sahibi hesabı açar.

    Args:
        email (str): Doğrulanmış giriş e-postası.
        password (str): Doğrulanmış ham parola.
        first_name (str): Ad.
        last_name (str): Soyad.
        phone (str): İsteğe bağlı telefon.

    Returns:
        User: Oluşturulan kullanıcı.
    """
    return create_user(email, password, first_name=first_name, last_name=last_name, phone=phone)


def update_profile(user, **changes):
    """
    Kullanıcının yalnızca izin verilen profil alanlarını günceller.

    Args:
        user (User): Güncellenecek kullanıcı.
        **changes (Any): Doğrulanmış alan değerleri; izinli olmayanlar yok sayılır.

    Returns:
        User: Güncellenmiş kullanıcı.
    """
    fields = [field for field in PROFILE_FIELDS if field in changes]
    for field in fields:
        setattr(user, field, changes[field])
    if fields:
        user.save(update_fields=fields)
    return user


def email_is_registered(email):
    """
    E-postanın (büyük/küçük harf duyarsız) kayıtlı bir hesaba ait olup olmadığını söyler.

    Args:
        email (str): Kontrol edilecek e-posta.

    Returns:
        bool: Kayıtlı bir hesap varsa True.
    """
    return get_user_model().objects.by_email(email).exists()


def list_users_for_admin():
    """
    Admin kullanıcı listesi için tüm kullanıcıları başvuru sayılarıyla döndürür.

    Returns:
        QuerySet[User]: `request_count` ile işaretlenmiş kullanıcılar.
    """
    return get_user_model().objects.with_request_count()
