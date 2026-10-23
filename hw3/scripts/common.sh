#!/bin/sh
set -eu

PROJECT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
cd "$PROJECT_DIR"

cli() { docker compose exec -T redis redis-cli --raw "$@"; }

show() {
  printf '\n$ redis-cli'
  for arg in "$@"; do printf ' %s' "$arg"; done
  printf '\n'
  result=$(docker compose exec -T redis redis-cli --raw "$@")
  if [ -n "$result" ]; then
    printf '%s\n' "$result"
  else
    printf '(nil/пусто)\n'
  fi
}
