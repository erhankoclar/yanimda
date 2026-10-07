from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers


class AdminUserSerializer(serializers.ModelSerializer):
    """Admin kullanıcı tablosu satırı ve detayı."""

    full_name = serializers.CharField(source='get_full_name', read_only=True, help_text=_('First and last name.'))
    request_count = serializers.IntegerField(read_only=True, help_text=_('Number of care requests created by the user.'))

    class Meta:
        model = get_user_model()
        fields = [
            'id', 'email', 'first_name', 'last_name', 'full_name', 'phone',
            'is_staff', 'is_active', 'date_joined', 'last_login', 'request_count',
        ]
        read_only_fields = fields
        extra_kwargs = {
            'email': {'help_text': _('Login email address.')},
            'phone': {'help_text': _('Profile phone number.')},
            'is_staff': {'help_text': _('True when the user can access the admin panel.')},
            'is_active': {'help_text': _('False when the account is disabled and cannot log in.')},
            'date_joined': {'help_text': _('Registration time.')},
            'last_login': {'help_text': _('Last successful login time; null if the user never logged in.')},
        }
