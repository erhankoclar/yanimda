#!/usr/bin/env bash
# Commit öncesi tam regresyon: backend, frontend ve e2e testleri.
# Kullanım: scripts/dev/check-all.sh [--no-e2e]
DIR="$(dirname "$0")"
status=0
echo "== Backend";  bash "$DIR/test-backend.sh"  || status=1
echo "== Frontend"; bash "$DIR/test-frontend.sh" || status=1
if [ "${1:-}" != "--no-e2e" ]; then
    echo "== E2E"; bash "$DIR/test-e2e.sh" || status=1
fi
[ "$status" -eq 0 ] && echo "SONUÇ: hepsi geçti" || echo "SONUÇ: hata var (ayrıntılar .dev-logs/)"
exit "$status"
