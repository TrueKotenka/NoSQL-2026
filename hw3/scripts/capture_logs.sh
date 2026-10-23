#!/bin/sh
set -eu
PROJECT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
cd "$PROJECT_DIR"
mkdir -p screenshots

{
  echo '$ docker compose ps'
  docker compose ps
} > screenshots/01_container.log

{
  echo '$ docker compose exec -T redis redis-cli PING'
  docker compose exec -T redis redis-cli PING
} > screenshots/02_connection.log

sh scripts/00_status.sh > screenshots/03_structures.log
sh scripts/02_ttl_counter.sh > screenshots/04_ttl_counter.log
sh scripts/03_collections.sh > screenshots/05_collections.log
sh scripts/04_transaction.sh > screenshots/06_transaction.log
sh scripts/05_cache.sh > screenshots/07_cache.log
sh scripts/06_persistence.sh > screenshots/08_persistence.log
sh scripts/07_memory.sh > screenshots/09_memory.log
sh scripts/01_basic.sh > screenshots/10_basic.log

echo 'Протоколы команд записаны в screenshots/*.log'
