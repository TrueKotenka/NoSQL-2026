#!/bin/sh
set -eu
. "$(dirname "$0")/common.sh"

table=$(mktemp)
trap 'rm -f "$table"' EXIT HUP INT TERM
for key in vidlab:user:1 vidlab:channel:1:recent vidlab:videos:rating; do
  type=$(cli TYPE "$key")
  bytes=$(cli MEMORY USAGE "$key" SAMPLES 0)
  printf '\n$ redis-cli TYPE %s\n%s\n' "$key" "$type"
  printf '$ redis-cli MEMORY USAGE %s SAMPLES 0\n%s\n' "$key" "$bytes"
  printf '%-37s | %-10s | %s\n' "$key" "$type" "$bytes" >> "$table"
done
printf '\n%-37s | %-10s | %s\n' 'Ключ' 'TYPE' 'MEMORY USAGE, байт'
printf '%s\n' '--------------------------------------------------------------------------'
cat "$table"
echo 'Значения зависят от версии Redis и способа размещения данных в памяти.'
