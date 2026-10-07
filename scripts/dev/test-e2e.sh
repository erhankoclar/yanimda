#!/usr/bin/env bash
# Playwright uçtan uca testlerini çalışan yığına (veya verilen adrese) karşı çalıştırır.
# Kullanım: scripts/dev/test-e2e.sh [https://site-adresi]
source "$(dirname "$0")/_common.sh"
ensure_stack
BASE_ARGS=()
if [ -n "${1:-}" ]; then
    BASE_ARGS=(-e "E2E_BASE_URL=$1")
fi
run_logged e2e '[0-9]+ (passed|failed|flaky)' '✘|Error:|expect\(' -- \
    docker compose --profile e2e run --rm "${BASE_ARGS[@]}" e2e
