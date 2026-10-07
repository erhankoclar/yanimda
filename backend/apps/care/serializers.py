from datetime import timedelta

from django.utils import timezone
from django.utils.translation import gettext
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from apps.care import api_descriptions, conf
from apps.care.models import CareRequest, ServiceType
from apps.care.validators import normalize_phone


class ServiceTypeSerializer(serializers.ModelSerializer):
    """Sihirbazda gösterilen hizmet kartının verileri."""

    class Meta:
        model = ServiceType
        fields = ['id', 'name', 'slug', 'description', 'icon']
        extra_kwargs = {
            'name': {'help_text': _('Service name shown on the card.')},
            'slug': {'help_text': _('Stable, URL safe service key.')},
            'description': {'help_text': _('Short explanation shown under the service name.')},
            'icon': {'help_text': _('Icon key mapped to an icon by the frontend, for example <code>companion</code>.')},
        }


class CareRequestSerializer(serializers.ModelSerializer):
    """Başvuru sahibinin kendi talebini oluşturması ve görüntülemesi için kullanılır."""

    service = serializers.PrimaryKeyRelatedField(
        queryset=ServiceType.objects.filter(is_active=True), write_only=True,
        help_text=api_descriptions.CARE_REQUEST_SERVICE_HELP_TEXT,
    )
    service_detail = ServiceTypeSerializer(source='service', read_only=True, help_text=_('Selected service type.'))
    consent = serializers.BooleanField(
        write_only=True,
        help_text=_('Must be <code>true</code>: the applicant accepts that the given personal data is processed '
                    'to plan the service. The acceptance time is stored.'),
    )
    status_display = serializers.CharField(
        source='get_status_display', read_only=True, help_text=_('Translated label of the status.'),
    )

    class Meta:
        model = CareRequest
        fields = [
            'id', 'service', 'service_detail',
            'elder_full_name', 'elder_age', 'relationship', 'elder_notes',
            'preferred_date', 'time_slot', 'city', 'district', 'address',
            'contact_phone', 'alternate_contact_name', 'alternate_contact_phone',
            'consent', 'status', 'status_display', 'created_at',
        ]
        read_only_fields = ['id', 'status', 'created_at']
        extra_kwargs = {
            'elder_full_name': {'help_text': _('Full name of the elder who will receive the service.')},
            'elder_age': {'help_text': _('Age of the elder, between 40 and 120.')},
            'relationship': {'help_text': _('How the applicant is related to the elder.')},
            'elder_notes': {'help_text': _('Optional health or care notes the team should know, '
                                           'for example walking support or hearing loss.')},
            'preferred_date': {'help_text': _('Preferred service date in YYYY-MM-DD format. '
                                              'Cannot be in the past or too far in the future.')},
            'time_slot': {'help_text': _('Preferred part of the day.')},
            'city': {'help_text': _('City of the service address.')},
            'district': {'help_text': _('District of the service address.')},
            'address': {'help_text': _('Open address where the service will be given.')},
            'contact_phone': {'help_text': _('Phone number to reach the applicant. 10-15 digits; spaces, '
                                             'parentheses and dashes are removed.')},
            'alternate_contact_name': {'help_text': _('Optional second person to call. '
                                                      'Required when an alternate phone is given.')},
            'alternate_contact_phone': {'help_text': _('Optional phone of the second person. '
                                                       'Required when an alternate name is given.')},
            'status': {'help_text': _('Processing status. Set to <code>new</code> on creation and '
                                      'changed only by the admin team.')},
            'created_at': {'help_text': _('Creation time of the request.')},
        }

    def validate_preferred_date(self, value):
        """
        Tercih edilen tarihin bugün ile izin verilen en ileri tarih arasında olduğunu doğrular.

        Args:
            value (date): İstekte gönderilen tarih.

        Returns:
            date: Değiştirilmemiş tarih.

        Raises:
            serializers.ValidationError: Tarih geçmişteyse veya izin verilen süreden ileriyse.
        """
        today = timezone.localdate()
        if value < today:
            raise serializers.ValidationError(gettext('The preferred date cannot be in the past.'))
        if value > today + timedelta(days=conf.MAX_PREFERRED_DAYS_AHEAD):
            raise serializers.ValidationError(
                gettext('The preferred date can be at most %(days)d days ahead.') % {
                    'days': conf.MAX_PREFERRED_DAYS_AHEAD,
                },
            )
        return value

    def validate_contact_phone(self, value):
        """
        Başvuru sahibinin telefonunu doğrulayıp normalleştirir.

        Args:
            value (str): Girilen telefon.

        Returns:
            str: Normalleştirilmiş telefon.

        Raises:
            serializers.ValidationError: Telefon geçersizse.
        """
        return normalize_phone(value)

    def validate_alternate_contact_phone(self, value):
        """
        Alternatif kişi telefonunu, girilmişse doğrulayıp normalleştirir.

        Args:
            value (str): Girilen telefon; boş olabilir.

        Returns:
            str: Normalleştirilmiş telefon veya boş metin.

        Raises:
            serializers.ValidationError: Telefon girilmiş ve geçersizse.
        """
        return normalize_phone(value) if value.strip() else ''

    def validate_consent(self, value):
        """
        Kişisel veri işleme onayının verildiğini doğrular.

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

    def validate(self, attrs):
        """
        Alternatif kişi adı ve telefonunun birlikte verildiğini doğrular.

        Args:
            attrs (dict[str, Any]): Alan doğrulamasından geçmiş veriler.

        Returns:
            dict[str, Any]: Değiştirilmemiş veriler.

        Raises:
            serializers.ValidationError: Ad ve telefondan yalnızca biri verilmişse ilgili eksik alan altında.
        """
        name = attrs.get('alternate_contact_name', '').strip()
        phone = attrs.get('alternate_contact_phone', '')
        if name and not phone:
            raise serializers.ValidationError(
                {'alternate_contact_phone': gettext('Enter the phone of the alternate contact.')},
            )
        if phone and not name:
            raise serializers.ValidationError(
                {'alternate_contact_name': gettext('Enter the name of the alternate contact.')},
            )
        return attrs

    def create(self, validated_data):
        """
        Talebi onay zamanını kaydederek oluşturur; başvuru sahibi view tarafından verilir.

        Args:
            validated_data (dict[str, Any]): Doğrulanmış veriler ve `applicant`.

        Returns:
            CareRequest: Oluşturulan talep.
        """
        validated_data.pop('consent')
        validated_data['consent_given_at'] = timezone.now()
        return super().create(validated_data)
