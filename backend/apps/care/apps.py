from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class CareConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.care'
    label = 'care'
    verbose_name = _('Care services')

    def ready(self):
        """
        Uygulama açılışında modül throttle oranlarını kaydeder.

        Throttle sınıfları istek sırasında oranları okuduğundan kayıt,
        endpoint import sırasından bağımsız olarak açılışta yapılır.
        """
        from apps.care.conf import register_throttle_rates

        register_throttle_rates()
