#!/bin/sh
set -eu
. "$(dirname "$0")/common.sh"

echo '$ docker compose up -d'
compose up -d
sh scripts/wait_for_cluster.sh 3 0

echo '$ docker compose exec -T cassandra1 cqlsh -f /workspace/cql/01_schema.cql'
cql_file 01_schema.cql
echo '$ docker compose exec -T cassandra1 cqlsh -f /workspace/cql/02_seed.cql'
cql_file 02_seed.cql

echo '$ docker compose exec -T cassandra1 cqlsh -e "SELECT COUNT(*) FROM shop_events.service_events;"'
compose exec -T cassandra1 env -u TZ cqlsh -e 'SELECT COUNT(*) FROM shop_events.service_events;'
