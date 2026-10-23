#!/bin/sh
set -eu
PROJECT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
for name in 00_status 01_basic 02_ttl_counter 03_collections 04_transaction 05_cache 06_persistence 07_memory; do
  printf '\n========== %s ==========\n' "$name"
  sh "$PROJECT_DIR/scripts/$name.sh"
done
