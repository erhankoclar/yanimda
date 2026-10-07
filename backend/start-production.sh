#!/bin/sh
# Üretim açılışı: migration, varsayılan veriler, (verilmişse) admin hesabı ve gunicorn.
set -e

python manage.py migrate --noinput
python manage.py care_create_defaults

if [ -n "$DJANGO_SUPERUSER_EMAIL" ] && [ -n "$DJANGO_SUPERUSER_PASSWORD" ]; then
    if python manage.py createsuperuser --noinput >/dev/null 2>&1; then
        echo "Admin hesabı oluşturuldu: $DJANGO_SUPERUSER_EMAIL"
    else
        echo "Admin hesabı zaten var: $DJANGO_SUPERUSER_EMAIL"
    fi
fi

exec gunicorn config.wsgi:application \
    --bind "0.0.0.0:${PORT:-8000}" \
    --workers "${WEB_CONCURRENCY:-2}" \
    --access-logfile - \
    --timeout 60
