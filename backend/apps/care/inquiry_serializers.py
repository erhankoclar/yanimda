from django.utils.translation import gettext
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from apps.care import api_descriptions
from apps.care.models import ServiceInquiry, ServiceType
from apps.care.serializers import ServiceTypeSerializer

NAME_MIN_LENGTH = 2
MESSAGE_MIN_LENGTH = 10
MESSAGE_MAX_LENGTH = 2000


class ServiceInquirySerializer(serializers.ModelSerializer):
    """Ana sayfadaki hesapsız hızlı talep formu."""

    full_name = serializers.CharField(
        max_length=150,
        help_text=_('Name and surname of the person to contact. At least 2 characters.'),
    )
    email = serializers.EmailField(help_text=_('Email address to reply to. Stored in lower case.'))
    service = serializers.PrimaryKeyRelatedField(
        queryset=ServiceType.objects.active(), write_only=True,
        help_text=api_descriptions.INQUIRY_SERVICE_HELP_TEXT,
    )
    service_detail = ServiceTypeSerializer(source='service', read_only=True, help_text=_('Requested service type.'))
    message = serializers.CharField(
        max_length=MESSAGE_MAX_LENGTH, trim_whitespace=True,
        help_text=_('Short description of the need, for example who needs support and when. '
                    'Between 10 and 2000 characters.'),
    )
    consent = serializers.BooleanField(
        write_only=True,
        help_text=_('Must be <code>true</code>: the person accepts that the given data is used to answer the '
                    'inquiry. The acceptance time is stored.'),
    )
    website = serializers.CharField(
        write_only=True, required=False, allow_blank=True,
        help_text=_('Spam trap. Leave empty; it is hidden from people in the form.'),
    )

    class Meta:
        model = ServiceInquiry
        fields = ['id', 'full_name', 'email', 'service', 'service_detail', 'message', 'consent', 'website', 'created_at']
        read_only_fields = ['id', 'created_at']
        extra_kwargs = {'created_at': {'help_text': _('Time the inquiry was stored.')}}

    def validate_full_name(self, value):
        """
        Ad soyadın boşluklar çıkarıldıktan sonra en az iki karakter olduğunu doğrular.

        Args:
            value (str): Girilen ad soyad.

        Returns:
            str: Fazla boşlukları temizlenmiş ad soyad.

        Raises:
            serializers.ValidationError: Ad soyad çok kısaysa.
        """
        cleaned = ' '.join(value.split())
        if len(cleaned) < NAME_MIN_LENGTH:
            raise serializers.ValidationError(gettext('Enter your name and surname.'))
        return cleaned

    def validate_email(self, value):
        """
        E-postayı küçük harfe çevirir.

        Args:
            value (str): Girilen e-posta.

        Returns:
            str: Küçük harfli e-posta.
        """
        return value.strip().lower()

    def validate_message(self, value):
        """
        Açıklamanın anlamlı uzunlukta olduğunu doğrular.

        Args:
            value (str): Girilen açıklama.

        Returns:
            str: Değiştirilmemiş açıklama.

        Raises:
            serializers.ValidationError: Açıklama çok kısaysa.
        """
        if len(value) < MESSAGE_MIN_LENGTH:
            raise serializers.ValidationError(
                gettext('Please describe the need in at least %(count)d characters.') % {'count': MESSAGE_MIN_LENGTH},
            )
        return value

    def validate_consent(self, value):
        """
        Kişisel veri kullanım onayının verildiğini doğrular.

        Args:
            value (bool): Onay değeri.

        Returns:
            bool: True.

        Raises:
            serializers.ValidationError: Onay verilmemişse.
        """
        if not value:
            raise serializers.ValidationError(gettext('You must accept the processing of personal data.'))
        return value

    def validate_website(self, value):
        """
        Spam tuzağı alanının boş kaldığını doğrular; dolu ise istek bot isteği sayılır.

        Args:
            value (str): Gizli alanın değeri.

        Returns:
            str: Boş metin.

        Raises:
            serializers.ValidationError: Alan doldurulmuşsa.
        """
        if value:
            raise serializers.ValidationError(gettext('The form could not be sent. Please try again.'))
        return value


class AdminServiceInquirySerializer(serializers.ModelSerializer):
    """Admin listesinde hızlı talebin tüm bilgileri."""

    service = ServiceTypeSerializer(read_only=True, help_text=_('Requested service type.'))

    class Meta:
        model = ServiceInquiry
        fields = ['id', 'full_name', 'email', 'service', 'message', 'consent_given_at', 'created_at']
        read_only_fields = fields
