#!/bin/sh
# Konteyner açılışında çevirileri derler, bekleyen migration'ları uygular ve
# varsayılan verileri (tekrar çalıştırılabilir) yükler.
set -e

python manage.py compilemessages -l tr --ignore ".venv" >/dev/null
python manage.py migrate --noinput
python manage.py care_create_defaults

exec "$@"
