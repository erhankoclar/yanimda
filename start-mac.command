#!/usr/bin/env bash
# macOS: Finder'da çift tıklayarak Yanımda'yı başlatır.
cd "$(dirname "$0")" && exec bash scripts/start-unix.sh "$@"
