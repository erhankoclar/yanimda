import os
from unittest.mock import patch

from django.conf import settings
from django.test import SimpleTestCase
from rest_framework.throttling import SimpleRateThrottle

from apps.accounts.conf import _DEFAULT_THROTTLE_RATES, get_throttle_rates
from apps.accounts.throttles import LoginRateThrottle, RegisterRateThrottle


class ThrottleConfTests(SimpleTestCase):
    def test_env_overrides_default_rate(self):
        """
        `THROTTLE_{SCOPE}` ortam değişkeninin varsayılan oranı ezdiğini doğrular.

        Senaryo:
        - `THROTTLE_ACCOUNTS_LOGIN` ortam değişkeni ayarlanır.

        Beklenti:
        - Giriş oranı ortam değeri, kayıt oranı varsayılan değer olmalıdır.
        """
        with patch.dict(os.environ, {'THROTTLE_ACCOUNTS_LOGIN': '3/minute'}):
            # Test, çalıştığı ortamda (ör. docker-compose) verilmiş olabilecek ezmelerden bağımsız olmalı.
            os.environ.pop('THROTTLE_ACCOUNTS_REGISTER', None)
            rates = get_throttle_rates()

        self.assertEqual(rates['accounts_login'], '3/minute')
        self.assertEqual(rates['accounts_register'], _DEFAULT_THROTTLE_RATES['accounts_register'])

    def test_scopes_are_registered_on_startup(self):
        """
        Throttle sınıflarının scope'larının açılışta kaydedildiğini doğrular.

        Senaryo:
        - Uygulama yüklendikten sonra DRF ayarları ve SimpleRateThrottle oranları okunur.

        Beklenti:
        - Her throttle sınıfının scope'u iki eşlemede de bulunmalıdır.
        """
        configured = settings.REST_FRAMEWORK['DEFAULT_THROTTLE_RATES']
        for throttle in (LoginRateThrottle, RegisterRateThrottle):
            self.assertIn(throttle.scope, configured)
            self.assertIn(throttle.scope, SimpleRateThrottle.THROTTLE_RATES)
