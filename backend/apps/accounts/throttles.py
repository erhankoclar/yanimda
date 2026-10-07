from rest_framework.throttling import AnonRateThrottle


class RegisterRateThrottle(AnonRateThrottle):
    """Kayıt isteklerini IP adresine göre sınırlar."""

    scope = 'accounts_register'


class LoginRateThrottle(AnonRateThrottle):
    """Giriş (token alma) isteklerini IP adresine göre sınırlar."""

    scope = 'accounts_login'
