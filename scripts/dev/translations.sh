#!/usr/bin/env bash
# Backend Türkçe çeviri kataloğunu yeniler, (verilirse) JSON'dan doldurur, eksik/bulanık girdileri listeler.
# Kullanım: scripts/dev/translations.sh [ceviriler.json]
#   JSON biçimi: {"English msgid": "Türkçe çeviri", ...}
source "$(dirname "$0")/_common.sh"
cd "$ROOT/backend"
PY=.venv/Scripts/python
[ -x "$PY" ] || PY=.venv/bin/python
"$PY" manage.py makemessages -l tr -e py -e html -e json -i ".venv/*" -i "venv/*" --no-location >/dev/null 2>&1
PO_FILL="$(cygpath -w "$ROOT/scripts/dev/po_fill.py" 2>/dev/null || echo "$ROOT/scripts/dev/po_fill.py")"
JSON_ARG="${1:+$(cygpath -w "$1" 2>/dev/null || echo "$1")}"
"$PY" -I "$PO_FILL" locale/tr/LC_MESSAGES/django.po ${JSON_ARG:+"$JSON_ARG"}
