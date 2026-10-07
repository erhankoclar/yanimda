from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class AccountsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.accounts'
    label = 'accounts'
    verbose_name = _('Accounts')

    def ready(self):
        """
        Uygulama açılışında modül throttle oranlarını kaydeder.

        Throttle sınıfları istek sırasında oranları okuduğundan kayıt,
        endpoint import sırasından bağımsız olarak açılışta yapılır.
        """
        from apps.accounts.conf import register_throttle_rates

        register_throttle_rates()
