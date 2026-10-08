#!/usr/bin/env bash
# Sayfaların 390, 820 ve 1366 px ekran görüntülerini .shots/<ad>/ altına alır.
# Kullanım: scripts/dev/screenshots.sh <ad> <oturum: none|applicant|admin> <yol> [yol...]
#   ör. scripts/dev/screenshots.sh admin-dashboard admin /admin/dashboard
# Ek ortam değişkenleri: THEME=light|dark (tarayıcı renk şeması), LOCALE=tr|en, BASE_URL,
#   CLICK=<css seçici> (çekimden önce tıklanır; ör. mobil menü düğmesi)
source "$(dirname "$0")/_common.sh"
ensure_stack
NAME="$1"; SESSION="$2"; shift 2
OUT="$ROOT/.shots/$NAME"
rm -rf "$OUT" && mkdir -p "$OUT"
docker compose --profile e2e run --rm \
    -e "SHOT_SESSION=$SESSION" -e "SHOT_PATHS=$*" -e "SHOT_THEME=${THEME:-light}" -e "SHOT_LOCALE=${LOCALE:-}" -e "SHOT_CLICK=${CLICK:-}" \
    -e "E2E_BASE_URL=${BASE_URL:-http://frontend:5173}" \
    -v "$(cygpath -w "$OUT" 2>/dev/null || echo "$OUT"):/shots" e2e sh -c "npm ci --silent --no-audit --no-fund >/dev/null 2>&1 && node scripts/screenshots.mjs" \
    2>&1 | grep -E '^(SHOT|ERROR|CONSOLE)'
echo "Görüntüler: .shots/$NAME/"
