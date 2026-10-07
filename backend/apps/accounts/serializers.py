from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from django.utils.translation import gettext
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from apps.accounts.services import user_service

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """Oturum açmış kullanıcının profil bilgilerini okur ve günceller."""

    email = serializers.EmailField(read_only=True, help_text=_('Login email address. Cannot be changed.'))
    first_name = serializers.CharField(
        max_length=150, required=False, allow_blank=True, help_text=_('First name of the user.'),
    )
    last_name = serializers.CharField(
        max_length=150, required=False, allow_blank=True, help_text=_('Last name of the user.'),
    )
    phone = serializers.CharField(
        max_length=20, required=False, allow_blank=True,
        help_text=_('Contact phone number, for example 05xx xxx xx xx. Optional, at most 20 characters.'),
    )
    is_staff = serializers.BooleanField(
        read_only=True, help_text=_('True when the user can access the admin panel. Read-only.'),
    )

    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name', 'phone', 'is_staff']
        read_only_fields = ['id']


class RegisterSerializer(serializers.ModelSerializer):
    """Yeni başvuru sahibi hesabı oluşturur."""

    email = serializers.EmailField(help_text=_('Email address used to log in. Must not be registered before.'))
    password = serializers.CharField(
        write_only=True, trim_whitespace=False, style={'input_type': 'password'},
        help_text=_('Account password. Must satisfy the password rules (at least 8 characters, not too common, '
                    'not entirely numeric). Never returned in responses.'),
    )
    first_name = serializers.CharField(max_length=150, help_text=_('First name of the applicant.'))
    last_name = serializers.CharField(max_length=150, help_text=_('Last name of the applicant.'))
    phone = serializers.CharField(
        max_length=20, required=False, allow_blank=True,
        help_text=_('Contact phone number. Optional, at most 20 characters.'),
    )

    class Meta:
        model = User
        fields = ['id', 'email', 'password', 'first_name', 'last_name', 'phone']
        read_only_fields = ['id']

    def validate_email(self, value):
        """
        E-postayı küçük harfe çevirir ve daha önce kayıtlı olmadığını doğrular.

        Args:
            value (str): İstekte gönderilen e-posta adresi.

        Returns:
            str: Küçük harfe çevrilmiş e-posta adresi.

        Raises:
            serializers.ValidationError: E-posta adresi zaten kayıtlıysa.
        """
        email = value.strip().lower()
        if user_service.email_is_registered(email):
            raise serializers.ValidationError(gettext('A user with this email address already exists.'))
        return email

    def validate(self, attrs):
        """
        Parolayı kullanıcı bilgileriyle birlikte Django parola kurallarına göre doğrular.

        Args:
            attrs (dict[str, Any]): Alan doğrulamasından geçmiş veriler.

        Returns:
            dict[str, Any]: Değiştirilmemiş doğrulanmış veriler.

        Raises:
            serializers.ValidationError: Parola kurallara uymadığında `password` alanı altında.
        """
        candidate = User(email=attrs['email'], first_name=attrs['first_name'], last_name=attrs['last_name'])
        try:
            validate_password(attrs['password'], user=candidate)
        except DjangoValidationError as error:
            raise serializers.ValidationError({'password': list(error.messages)}) from error
        return attrs
