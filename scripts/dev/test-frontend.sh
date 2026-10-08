#!/usr/bin/env bash
# Frontend (Vitest) testlerini Docker'da çalıştırır ve yalnızca özeti gösterir.
# Kullanım: scripts/dev/test-frontend.sh [test yolu...]   ör. tests/security
source "$(dirname "$0")/_common.sh"
ensure_stack
run_logged frontend 'Test Files|Tests ' '×|FAIL|AssertionError|Error:' -- \
    docker compose exec -T frontend npx vitest run "$@"
