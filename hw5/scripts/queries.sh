#!/bin/sh
set -eu
. "$(dirname "$0")/common.sh"

for file in 03_hour.cql 04_error.cql; do
  printf '\n$ docker compose exec -T cassandra1 cqlsh -f /workspace/cql/%s\n' "$file"
  cat "cql/$file"
  cql_file "$file"
done
