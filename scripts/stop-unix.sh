#!/usr/bin/env bash
# Yanımda servislerini durdurur. Veriler silinmez.
set -euo pipefail

cd "$(dirname "$0")/.."

if docker info >/dev/null 2>&1; then
    docker compose down
else
    sudo docker compose down
fi
