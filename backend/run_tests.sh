#!/bin/sh
# Backend testlerini çalıştırır.
#
# Kullanım:
#   ./run_tests.sh                 -> tüm testler
#   ./run_tests.sh security        -> tüm uygulamalardaki yalnızca security testleri
#   ./run_tests.sh unit contract   -> birden fazla tür
#
# Türler: unit, integration, security, regression, contract, performance
set -e
cd "$(dirname "$0")"

if [ "$#" -eq 0 ]; then
    exec python manage.py test apps config
fi

labels=""
for test_type in "$@"; do
    for dir in apps/*/tests/"$test_type" config/tests/"$test_type"; do
        if [ -d "$dir" ]; then
            labels="$labels $(echo "$dir" | tr '/' '.')"
        fi
    done
done

if [ -z "$labels" ]; then
    echo "Bu türde test bulunamadı: $*" >&2
    exit 1
fi

# shellcheck disable=SC2086
exec python manage.py test $labels
