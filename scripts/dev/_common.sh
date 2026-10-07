#!/usr/bin/env bash
# Geliştirme betiklerinin ortak yardımcıları. Doğrudan çalıştırılmaz; diğer betikler içe aktarır.

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
LOG_DIR="$ROOT/.dev-logs"
mkdir -p "$LOG_DIR"
cd "$ROOT"

# Git Bash'te Docker'a verilen /yolların Windows yoluna çevrilmesini engeller.
export MSYS_NO_PATHCONV=1

# Yığın ayakta değilse sırayla başlatır.
ensure_stack() {
    if ! docker compose ps --status running --services 2>/dev/null | grep -q '^frontend$'; then
        echo "Yığın başlatılıyor..."
        docker compose up -d --wait >/dev/null 2>&1 || { echo "HATA: docker compose up başarısız"; exit 1; }
    fi
}

# Komutu çalıştırır, çıktıyı log dosyasına yazar, ekrana yalnızca özet satırlarını basar.
# Kullanım: run_logged <log adı> <özet regex> <hata regex> -- komut...
run_logged() {
    local name="$1" summary="$2" failure="$3"
    shift 4
    local log="$LOG_DIR/$name.log"
    "$@" >"$log" 2>&1
    local code=$?
    grep -E "$summary" "$log" | sed 's/\x1b\[[0-9;]*m//g' | tail -5
    if [ "$code" -ne 0 ]; then
        echo "--- Hatalar ($log):"
        grep -E "$failure" "$log" | sed 's/\x1b\[[0-9;]*m//g' | head -40
    fi
    return "$code"
}
