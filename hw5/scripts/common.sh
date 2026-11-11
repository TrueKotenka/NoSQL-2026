#!/bin/sh
set -eu

PROJECT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
cd "$PROJECT_DIR"

compose() { docker compose "$@"; }
cql_file() { compose exec -T cassandra1 env -u TZ cqlsh -f "/workspace/cql/$1"; }
