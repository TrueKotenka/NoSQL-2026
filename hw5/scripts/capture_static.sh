#!/bin/sh
set -eu
. "$(dirname "$0")/common.sh"
mkdir -p screenshots

{
  echo '$ docker compose ps'
  compose ps
  echo '$ docker compose exec -T cassandra1 nodetool status'
  compose exec -T cassandra1 nodetool status
} > screenshots/01_cluster.log

{
  echo '$ docker compose exec -T cassandra1 cqlsh'
  echo 'SHOW HOST'
  echo 'USE shop_events;'
  echo 'DESCRIBE TABLE service_events'
  echo 'DESCRIBE INDEX service_events_error_code_idx'
  printf 'SHOW HOST\nUSE shop_events;\nDESCRIBE TABLE service_events\nDESCRIBE INDEX service_events_error_code_idx\n' |
    compose exec -T cassandra1 env -u TZ cqlsh
} > screenshots/02_schema.log

{
  echo '$ docker compose exec -T cassandra1 cqlsh -f /workspace/cql/03_hour.cql'
  cat cql/03_hour.cql
  cql_file 03_hour.cql
} > screenshots/03_hour.log

{
  echo '$ docker compose exec -T cassandra1 cqlsh -f /workspace/cql/04_error.cql'
  cat cql/04_error.cql
  cql_file 04_error.cql
} > screenshots/04_error.log

echo 'Статические протоколы сохранены в screenshots/01–04_*.log'
