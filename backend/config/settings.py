"""
Yanımda API projesinin Django ayarları.

Ortama bağlı tüm değerler `.env` dosyasından veya ortam değişkenlerinden okunur.
Örnek değerler için `backend/.env.example` dosyasına bakın.
"""

from datetime import timedelta
from pathlib import Path

import environ
from django.utils.translation import gettext_lazy as _

BASE_DIR = Path(__file__).resolve().parent.parent

env = environ.Env(
    DEBUG=(bool, False),
    ALLOWED_HOSTS=(list, ['localhost', '127.0.0.1']),
    CORS_ALLOWED_ORIGINS=(list, ['http://localhost:5173', 'http://127.0.0.1:5173']),
)
environ.Env.read_env(BASE_DIR / '.env')

SECRET_KEY = env('SECRET_KEY', default='django-insecure-yanimda-dev-only-change-me')
DEBUG = env('DEBUG')
ALLOWED_HOSTS = env('ALLOWED_HOSTS')
# Render, servisin dış adresini bu değişkenle verir.
RENDER_EXTERNAL_HOSTNAME = env('RENDER_EXTERNAL_HOSTNAME', default='')
if RENDER_EXTERNAL_HOSTNAME:
    ALLOWED_HOSTS.append(RENDER_EXTERNAL_HOSTNAME)

INSTALLED_APPS = [
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.staticfiles',
    'corsheaders',
    'rest_framework',
    'rest_framework_simplejwt',
    'rest_framework_simplejwt.token_blacklist',
    'drf_spectacular',
    'django_filters',
    'parler',
    'apps.accounts',
    'apps.care',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

# Proje yalnızca PostgreSQL ile çalışır; varsayılan değer docker-compose'daki
# veritabanına makineden (5433 portu) bağlanır.
DATABASES = {
    'default': env.db('DATABASE_URL', default='postgres://yanimda:yanimda@localhost:5433/yanimda'),
}

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'tr'
LANGUAGES = [
    ('tr', _('Turkish')),
    ('en', _('English')),
]
LOCALE_PATHS = [BASE_DIR / 'locale']

# Kullanıcıya gösterilen içerik çevirileri (ör. hizmet adları) django-parler ile tutulur:
# her dil çeviri tablosunda bir satırdır. Etkin dil Django'nun dilinden (Accept-Language) gelir,
# çevirisi olmayan dilde Türkçeye düşülür.
PARLER_DEFAULT_LANGUAGE_CODE = 'tr'
PARLER_LANGUAGES = {
    None: tuple({'code': code} for code, _name in LANGUAGES),
    'default': {'fallbacks': ['tr'], 'hide_untranslated': False},
}
# Çeviriler sorgularda önceden yüklendiği için parler'in önbelleği kapalıdır; önbellek, çeviri
# değiştirildiğinde başka süreçlerde ve testlerde bayat metin gösterebiliyordu.
PARLER_ENABLE_CACHING = False
TIME_ZONE = 'Europe/Istanbul'
USE_I18N = True
USE_TZ = True

STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Üretimde derlenmiş Vue sitesi (vite build çıktısı) bu klasörden, API ile aynı adresten sunulur.
# Klasör yoksa (yerel geliştirme) site Vite geliştirme sunucusundan gelir.
FRONTEND_DIST_DIR = Path(env('FRONTEND_DIST_DIR', default=str(BASE_DIR / 'frontend_dist')))
WHITENOISE_ROOT = FRONTEND_DIST_DIR if FRONTEND_DIST_DIR.is_dir() else None

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

AUTH_USER_MODEL = 'accounts.User'

CORS_ALLOWED_ORIGINS = env('CORS_ALLOWED_ORIGINS')
CSRF_TRUSTED_ORIGINS = env.list('CSRF_TRUSTED_ORIGINS', default=[])
if RENDER_EXTERNAL_HOSTNAME:
    CSRF_TRUSTED_ORIGINS.append(f'https://{RENDER_EXTERNAL_HOSTNAME}')

# Üretim güvenliği: TLS'i önündeki vekil (Render) sonlandırır.
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_REFERRER_POLICY = 'same-origin'
SESSION_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_SECURE = not DEBUG
SECURE_SSL_REDIRECT = env.bool('SECURE_SSL_REDIRECT', default=False)
SECURE_HSTS_SECONDS = env.int('SECURE_HSTS_SECONDS', default=0)

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': ['rest_framework_simplejwt.authentication.JWTAuthentication'],
    'DEFAULT_PERMISSION_CLASSES': ['rest_framework.permissions.IsAuthenticated'],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    'PAGE_SIZE': 20,
}

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=env.int('JWT_ACCESS_MINUTES', default=15)),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=env.int('JWT_REFRESH_DAYS', default=7)),
    'ROTATE_REFRESH_TOKENS': True,
    # Döndürülen eski refresh token tekrar kullanılamaz.
    'BLACKLIST_AFTER_ROTATION': True,
    'UPDATE_LAST_LOGIN': True,
}

# Swagger / ReDoc: varsayılan olarak yalnızca DEBUG açıkken yayınlanır.
API_DOCS_ENABLED = env.bool('API_DOCS_ENABLED', default=DEBUG)

SPECTACULAR_SETTINGS = {
    'TITLE': 'Yanımda API',
    'DESCRIPTION': 'Yaşlı yakınları adına hizmet başvurusu ve yönetimi API servisi.',
    'VERSION': '0.1.0',
    'SERVE_INCLUDE_SCHEMA': False,
    'COMPONENT_SPLIT_REQUEST': True,
    'SWAGGER_UI_SETTINGS': {
        'persistAuthorization': True,
        'displayOperationId': True,
        'filter': True,
    },
}

# Fabrikaların (testler) ve demo verisinin hesaplara yazdığı parolalar; koda gömülmez,
# ortam değişkeniyle dışarıdan değiştirilebilir. Yalnızca kurgusal hesaplarda kullanılır.
TEST_USER_PASSWORD = env.str('TEST_USER_PASSWORD', default='Yanimda-Guclu-2026')
DEMO_USER_PASSWORD = env.str('DEMO_USER_PASSWORD', default='Kurgusal-Demo-2026')
