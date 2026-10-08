#!/bin/sh
# Konteyner açılışında çevirileri derler, bekleyen migration'ları uygular ve
# varsayılan verileri (tekrar çalıştırılabilir) yükler.
set -e

python manage.py compilemessages -l tr --ignore ".venv" >/dev/null
python manage.py migrate --noinput
python manage.py geo_create_defaults
python manage.py care_create_defaults

# Yalnızca yerel geliştirme için: e-posta ve parola verilmişse ve hesap yoksa admin oluşturulur.
if [ -n "$DJANGO_SUPERUSER_EMAIL" ] && [ -n "$DJANGO_SUPERUSER_PASSWORD" ]; then
    if python manage.py createsuperuser --noinput >/dev/null 2>&1; then
        echo "Admin hesabı oluşturuldu: $DJANGO_SUPERUSER_EMAIL"
    else
        echo "Admin hesabı zaten var: $DJANGO_SUPERUSER_EMAIL"
    fi
fi

exec "$@"
