#!/bin/sh
# Konteyner açılışında çevirileri derler ve bekleyen migration'ları uygular.
set -e

python manage.py compilemessages -l tr --ignore ".venv" >/dev/null
python manage.py migrate --noinput

exec "$@"
