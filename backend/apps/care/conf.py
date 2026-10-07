"""
care modülünün ayarları.

Throttle scope'ları `THROTTLE_{SCOPE.upper()}`, iş kuralları ise
`CARE_{AYAR}` ortam değişkenleriyle ezilebilir.
"""

import os

from django.conf import settings
from rest_framework.throttling import SimpleRateThrottle

_DEFAULT_THROTTLE_RATES = {
    'care_request_create': '20/day',
}

# Tercih edilen tarihin bugünden en fazla kaç gün sonrası olabileceği.
MAX_PREFERRED_DAYS_AHEAD = int(os.environ.get('CARE_MAX_PREFERRED_DAYS_AHEAD') or 90)


def get_throttle_rates():
    """
    Varsayılan oranları ortam değişkeni ezmeleriyle birleştirir.

    Returns:
        dict[str, str]: Scope adından orana eşleme.
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
    configured = settings.REST_FRAMEWORK.setdefault('DEFAULT_THROTTLE_RATES', {})
    for scope, rate in get_throttle_rates().items():
        configured.setdefault(scope, rate)
    SimpleRateThrottle.THROTTLE_RATES = {**SimpleRateThrottle.THROTTLE_RATES, **configured}
