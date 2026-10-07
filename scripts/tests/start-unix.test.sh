#!/usr/bin/env bash
# scripts/start-unix.sh için senaryo testleri.
#
# Gerçek Docker, sudo, curl vb. yerine çağrıları kaydeden sahte komutlar
# kullanılır; böylece kurulum dahil tüm akışlar güvenle denenir.
#
# Çalıştırma (Docker ile, herhangi bir işletim sisteminde):
#   docker run --rm -v "$PWD:/src:ro" ubuntu:24.04 bash /src/scripts/tests/start-unix.test.sh
set -uo pipefail

SRC="$(cd "$(dirname "$0")/../.." && pwd)"
PASS=0
FAIL=0

# Her senaryo için projenin kopyasını ve sahte komut klasörünü hazırlar.
setup() {
    WORK="$(mktemp -d)"
    mkdir -p "$WORK/project/scripts" "$WORK/bin"
    cp "$SRC/scripts/start-unix.sh" "$WORK/project/scripts/"
    LOG="$WORK/calls.log"
    : > "$LOG"
    export LOG STUB_BIN="$WORK/bin"
    export FAKE_OS=Linux DOCKER_RUNNING=1 DOCKER_SUDO_ONLY=0 COMPOSE_EXIT=0 FAKE_ARCH=x86_64

    stub() {
        printf '#!/usr/bin/env bash\n%s\n' "$2" > "$WORK/bin/$1"
        chmod +x "$WORK/bin/$1"
    }

    # docker: info sonucu ortam değişkenleriyle, compose sonucu COMPOSE_EXIT ile belirlenir.
    cat > "$WORK/docker.real" <<'EOF'
#!/usr/bin/env bash
echo "${SUDO:+sudo }docker $*" >> "$LOG"
case "$1" in
    info)
        [ "$DOCKER_RUNNING" = 1 ] && exit 0
        # Docker Desktop açıldıktan sonra (open -a Docker) motor hazır sayılır.
        [ -f "$STUB_BIN/../docker-started" ] && exit 0
        [ "$DOCKER_SUDO_ONLY" = 1 ] && [ -n "${SUDO:-}" ] && exit 0
        exit 1 ;;
    compose)
        [ "$2" = "version" ] && exit 0
        exit "$COMPOSE_EXIT" ;;
esac
EOF
    chmod +x "$WORK/docker.real"
    cp "$WORK/docker.real" "$WORK/bin/docker"

    # Bulunamayan komutlar (ör. macOS kurulum dosyası) yalnızca kaydedilir.
    stub sudo 'echo "sudo $*" >> "$LOG"; command -v "$1" >/dev/null 2>&1 || exit 0; SUDO=1 exec "$@"'
    stub uname 'if [ "$1" = "-m" ]; then echo "$FAKE_ARCH"; else echo "$FAKE_OS"; fi'
    stub sleep 'exit 0'
    stub xdg-open 'echo "xdg-open $*" >> "$LOG"'
    stub open 'echo "open $*" >> "$LOG"'
    stub systemctl 'echo "systemctl $*" >> "$LOG"'
    stub usermod 'echo "usermod $*" >> "$LOG"'
    stub hdiutil 'echo "hdiutil $*" >> "$LOG"'
    # get.docker.com betiği yerine docker'ı "kuran" sahte bir betik indirir.
    stub curl 'echo "curl $*" >> "$LOG"
out=""; prev=""
for arg in "$@"; do [ "$prev" = "-o" ] && out="$arg"; prev="$arg"; done
[ -n "$out" ] && printf "cp %s %s\n" "'"$WORK"'/docker.real" "$STUB_BIN/docker" > "$out"
exit 0'
}

# Projeyi sahte komutlarla çalıştırır; çıktı $OUT, çıkış kodu $CODE olur.
run() {
    OUT="$(cd "$WORK/project" && PATH="$WORK/bin:/usr/bin:/bin" USER=tester bash scripts/start-unix.sh "$@" 2>&1)"
    CODE=$?
}

check() {
    local name="$1" condition="$2"
    if eval "$condition"; then
        PASS=$((PASS + 1))
        echo "  ok   - $name"
    else
        FAIL=$((FAIL + 1))
        echo "  FAIL - $name"
        echo "         koşul: $condition"
        echo "         çağrılar:"; sed 's/^/           /' "$LOG"
        echo "         çıktı:"; echo "$OUT" | sed 's/^/           /' | tail -5
    fi
}

called() { grep -qF -- "$1" "$LOG"; }

echo "Senaryo: Linux, Docker kurulu ve çalışıyor"
setup; run
check "başarıyla biter" '[ "$CODE" -eq 0 ]'
check "compose sıralı başlatılır" 'called "docker compose up -d --build --wait"'
check "kurulum yapılmaz" '! called "curl"'
check "site tarayıcıda açılır" 'called "xdg-open http://localhost:5173"'
check "giriş bilgileri yazdırılır" '[[ "$OUT" == *"admin@yanimda.local"* ]]'

echo "Senaryo: Linux, Docker kurulu değil"
setup; rm "$WORK/bin/docker"; run
check "başarıyla biter" '[ "$CODE" -eq 0 ]'
check "resmi kurulum betiği indirilir" 'called "curl -fsSL https://get.docker.com"'
check "kurulum sudo ile çalışır" 'called "sudo sh"'
check "servis etkinleştirilir" 'called "systemctl enable --now docker"'
check "kullanıcı docker grubuna eklenir" 'called "usermod -aG docker tester"'
check "kurulumdan sonra compose çalışır" 'called "docker compose up -d --build --wait"'

echo "Senaryo: Linux, Docker yalnızca sudo ile erişilebilir"
setup; DOCKER_RUNNING=0 DOCKER_SUDO_ONLY=1; export DOCKER_RUNNING DOCKER_SUDO_ONLY; run
check "başarıyla biter" '[ "$CODE" -eq 0 ]'
check "compose sudo ile çalışır" 'called "sudo docker compose up -d --build --wait"'

echo "Senaryo: macOS, Docker yok, Homebrew var"
setup; export FAKE_OS=Darwin; rm "$WORK/bin/docker"
cat > "$WORK/bin/brew" <<EOF
#!/usr/bin/env bash
echo "brew \$*" >> "\$LOG"; cp "$WORK/docker.real" "$WORK/bin/docker"
EOF
chmod +x "$WORK/bin/brew"; run
check "başarıyla biter" '[ "$CODE" -eq 0 ]'
check "Homebrew ile kurulur" 'called "brew install --cask docker"'
check "site open ile açılır" 'called "open http://localhost:5173"'

echo "Senaryo: macOS (Apple Silicon), Docker yok, Homebrew yok"
setup; export FAKE_OS=Darwin FAKE_ARCH=arm64; rm "$WORK/bin/docker"
cat > "$WORK/bin/hdiutil" <<EOF
#!/usr/bin/env bash
echo "hdiutil \$*" >> "\$LOG"; cp "$WORK/docker.real" "$WORK/bin/docker"
EOF
chmod +x "$WORK/bin/hdiutil"; run
check "başarıyla biter" '[ "$CODE" -eq 0 ]'
check "arm64 kurulum dosyası indirilir" 'called "https://desktop.docker.com/mac/main/arm64/Docker.dmg"'
check "dmg bağlanır" 'called "hdiutil attach"'
check "lisans kabul edilerek kurulur" 'called "install --accept-license --user tester"'

echo "Senaryo: macOS, Docker kurulu ama kapalı"
setup; export FAKE_OS=Darwin DOCKER_RUNNING=0
# open -a Docker çağrıldıktan sonra docker hazır olur.
cat > "$WORK/bin/open" <<'EOF'
#!/usr/bin/env bash
echo "open $*" >> "$LOG"
[ "$*" = "-a Docker" ] && touch "$STUB_BIN/../docker-started"
exit 0
EOF
chmod +x "$WORK/bin/open"; run
check "Docker Desktop açılır" 'called "open -a Docker"'
check "hazır olunca compose çalışır" 'called "docker compose up -d --build --wait"'

echo "Senaryo: --no-browser"
setup; run --no-browser
check "başarıyla biter" '[ "$CODE" -eq 0 ]'
check "tarayıcı açılmaz" '! called "xdg-open"'

echo "Senaryo: desteklenmeyen işletim sistemi"
setup; export FAKE_OS=MINGW64_NT; run
check "hata koduyla biter" '[ "$CODE" -ne 0 ]'
check "Windows betiğine yönlendirir" '[[ "$OUT" == *"start-windows.bat"* ]]'
check "compose çalışmaz" '! called "compose up"'

echo "Senaryo: compose başarısız"
setup; export COMPOSE_EXIT=1; run
check "hata koduyla biter" '[ "$CODE" -ne 0 ]'
check "log komutunu önerir" '[[ "$OUT" == *"docker compose logs"* ]]'
check "tarayıcı açılmaz" '! called "xdg-open"'

echo
echo "Sonuç: $PASS geçti, $FAIL başarısız"
[ "$FAIL" -eq 0 ]
