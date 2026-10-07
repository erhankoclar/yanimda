#!/usr/bin/env bash
# Yanımda'yı macOS veya Linux'ta tek adımda çalıştırır.
#
#   1. Docker kurulu değilse kurar (macOS: Homebrew veya resmi .dmg, Linux: get.docker.com).
#   2. Docker çalışmıyorsa başlatır ve hazır olmasını bekler.
#   3. docker compose ile veritabanı, backend ve frontend'i sırayla ayağa kaldırır.
#   4. Siteyi varsayılan tarayıcıda açar.
#
# Kullanım: scripts/start-unix.sh [--no-browser]
set -euo pipefail

cd "$(dirname "$0")/.."

APP_URL="http://localhost:5173"
OPEN_BROWSER=1
if [ "${1:-}" = "--no-browser" ]; then
    OPEN_BROWSER=0
fi
DOCKER=(docker)

step() {
    printf '\n\033[32m==> %s\033[0m\n' "$1"
}

fail() {
    printf '\n\033[31mHATA: %s\033[0m\n' "$1" >&2
    exit 1
}

install_docker_mac() {
    step "Docker bulunamadı. Docker Desktop kuruluyor (parolanız istenebilir)..."
    if command -v brew >/dev/null 2>&1; then
        brew install --cask docker
    else
        local arch dmg
        arch="$(uname -m)"
        [ "$arch" = "arm64" ] || arch="amd64"
        dmg="$(mktemp -d)/Docker.dmg"
        echo "Kurulum dosyası indiriliyor ($arch)..."
        curl -fL --progress-bar -o "$dmg" "https://desktop.docker.com/mac/main/$arch/Docker.dmg"
        hdiutil attach -nobrowse -quiet -mountpoint /Volumes/Docker "$dmg"
        sudo /Volumes/Docker/Docker.app/Contents/MacOS/install --accept-license --user "$USER"
        hdiutil detach -quiet /Volumes/Docker
    fi
}

install_docker_linux() {
    step "Docker bulunamadı. Docker Engine kuruluyor (sudo parolanız istenebilir)..."
    command -v curl >/dev/null 2>&1 || fail "Kurulum için curl gerekli. Önce curl kurun (ör. sudo apt install curl)."
    local installer
    installer="$(mktemp)"
    curl -fsSL https://get.docker.com -o "$installer"
    sudo sh "$installer"
    rm -f "$installer"
    sudo systemctl enable --now docker 2>/dev/null || sudo service docker start
    sudo usermod -aG docker "$USER" || true
}

wait_for_docker() {
    local seconds=0
    until "${DOCKER[@]}" info >/dev/null 2>&1; do
        if [ "$seconds" -ge 240 ]; then
            return 1
        fi
        sleep 3
        seconds=$((seconds + 3))
        printf '.'
    done
    echo " Docker hazır."
}

start_docker_mac() {
    docker info >/dev/null 2>&1 && return
    step "Docker Desktop başlatılıyor..."
    open -a Docker
    wait_for_docker || fail "Docker 4 dakika içinde hazır olmadı. Docker Desktop'ı açıp lisansı onaylayın ve betiği tekrar çalıştırın."
}

start_docker_linux() {
    docker info >/dev/null 2>&1 && return
    # Kullanıcı docker grubuna yeni eklendiyse bu oturumda sudo gerekir.
    if ! sudo docker info >/dev/null 2>&1; then
        step "Docker servisi başlatılıyor..."
        sudo systemctl start docker 2>/dev/null || sudo service docker start
    fi
    DOCKER=(sudo docker)
    wait_for_docker || fail "Docker servisi başlatılamadı. 'sudo systemctl status docker' çıktısına bakın."
}

open_browser() {
    [ "$OPEN_BROWSER" -eq 1 ] || return 0
    case "$OS" in
        Darwin) open "$APP_URL" ;;
        Linux)
            if command -v xdg-open >/dev/null 2>&1; then
                xdg-open "$APP_URL" >/dev/null 2>&1 &
            else
                echo "Tarayıcınızda şu adresi açın: $APP_URL"
            fi
            ;;
    esac
}

OS="$(uname -s)"
case "$OS" in
    Darwin)
        if ! command -v docker >/dev/null 2>&1 && [ -x /Applications/Docker.app/Contents/Resources/bin/docker ]; then
            export PATH="/Applications/Docker.app/Contents/Resources/bin:$PATH"
        fi
        command -v docker >/dev/null 2>&1 || install_docker_mac
        export PATH="/Applications/Docker.app/Contents/Resources/bin:$PATH"
        start_docker_mac
        ;;
    Linux)
        command -v docker >/dev/null 2>&1 || install_docker_linux
        start_docker_linux
        ;;
    *)
        fail "Desteklenmeyen işletim sistemi: $OS. Windows'ta start-windows.bat kullanın."
        ;;
esac

"${DOCKER[@]}" compose version >/dev/null 2>&1 || fail "Docker Compose eklentisi bulunamadı. Docker'ı güncelleyin."

step "Servisler sırayla başlatılıyor: veritabanı -> backend -> frontend (ilk açılış birkaç dakika sürebilir)..."
"${DOCKER[@]}" compose up -d --build --wait || fail "Servisler başlatılamadı. Ayrıntı için: docker compose logs"

step "Yanımda hazır"
echo "  Site          : $APP_URL"
echo "  Admin paneli  : $APP_URL/admin"
echo "  API belgeleri : http://localhost:8000/api/docs/"
echo "  Admin girişi  : admin@yanimda.local / Yanimda-Admin-2026 (yalnızca yerel geliştirme)"
echo "  Durdurmak için: stop-mac.command veya ./stop-linux.sh"

open_browser
