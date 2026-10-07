#!/usr/bin/env bash
# Linux: Yanımda'yı başlatır.
cd "$(dirname "$0")" && exec bash scripts/start-unix.sh "$@"
