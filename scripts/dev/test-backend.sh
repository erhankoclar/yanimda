#!/usr/bin/env bash
# Backend testlerini Docker'da (PostgreSQL) çalıştırır ve yalnızca özeti gösterir.
# Kullanım: scripts/dev/test-backend.sh [tür...]   ör. unit security
source "$(dirname "$0")/_common.sh"
ensure_stack
run_logged backend '^(Ran|OK|FAILED)' '^(FAIL|ERROR):|Error|assert' -- \
    docker compose exec -T backend sh run_tests.sh "$@"
