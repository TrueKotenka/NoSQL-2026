#!/bin/sh
set -eu
. "$(dirname "$0")/common.sh"

expected_up=${1:-3}
expected_down=${2:-0}
attempt=0
while [ "$attempt" -lt 120 ]; do
  status=$(compose exec -T cassandra1 nodetool status 2>/dev/null || true)
  up=$(printf '%s\n' "$status" | awk '$1 == "UN" {n++} END {print n+0}')
  down=$(printf '%s\n' "$status" | awk '$1 == "DN" {n++} END {print n+0}')
  if [ "$up" -eq "$expected_up" ] && [ "$down" -eq "$expected_down" ]; then
    printf '$ docker compose exec -T cassandra1 nodetool status\n%s\n' "$status"
    exit 0
  fi
  attempt=$((attempt + 1))
  sleep 5
done

printf 'Ожидалось UN=%s, DN=%s. Последний nodetool status:\n%s\n' "$expected_up" "$expected_down" "$status" >&2
exit 1
