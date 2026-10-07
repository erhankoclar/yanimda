"""
accounts modülünün throttle ayarları.

Her scope için varsayılan oran tanımlıdır; `THROTTLE_{SCOPE.upper()}` ortam
değişkeni ile ezilebilir.
"""

import os

from django.conf import settings
from rest_framework.throttling import SimpleRateThrottle

_DEFAULT_THROTTLE_RATES = {
    'accounts_register': '10/hour',
    'accounts_login': '10/minute',
}


def get_throttle_rates():
    """
    Varsayılan oranları ortam değişkeni ezmeleriyle birleştirir.

    Returns:
        dict[str, str]: Scope adından orana (ör. `10/minute`) eşleme.
    """
    rates = {}
    for scope, rate in _DEFAULT_THROTTLE_RATES.items():
        rates[scope] = os.environ.get(f'THROTTLE_{scope.upper()}') or rate
    return rates


def register_throttle_rates():
    """
    Modül oranlarını DRF ayarlarına ve SimpleRateThrottle sınıfına kaydeder.

    Proje ayarlarında aynı scope zaten tanımlıysa proje değeri korunur.
    """
    rest_framework = settings.REST_FRAMEWORK
    configured = rest_framework.setdefault('DEFAULT_THROTTLE_RATES', {})
    for scope, rate in get_throttle_rates().items():
        configured.setdefault(scope, rate)
    SimpleRateThrottle.THROTTLE_RATES = {**SimpleRateThrottle.THROTTLE_RATES, **configured}
