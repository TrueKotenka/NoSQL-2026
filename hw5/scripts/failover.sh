#!/bin/sh
set -eu
. "$(dirname "$0")/common.sh"

READ_ID=00000000-0000-4000-8000-000000000008
READ_CQL="SELECT service, event_day, event_time, event_id, message FROM shop_events.service_events WHERE service = 'checkout' AND event_day = '2026-11-10' AND event_time = '2026-11-10T10:15:00+0000' AND event_id = $READ_ID;"
WRITE_TIME=2026-11-11T12:00:00+0000
matrix=$(mktemp)
errors=$(mktemp)
node_stopped=0
unexpected=0

cleanup() {
  if [ "$node_stopped" -eq 1 ]; then
    compose start cassandra3 >/dev/null 2>&1 || true
  fi
  rm -f "$matrix" "$errors"
}
trap cleanup 0 1 2 15

cql() {
  level=$1
  statement=$2
  printf 'CONSISTENCY %s\n%s\n' "$level" "$statement" |
    compose exec -T cassandra1 env -u TZ cqlsh --request-timeout=20 2>&1
}

has_cql_error() {
  printf '%s\n' "$1" | grep -Eiq 'Error from server|Unavailable|WriteTimeout|ReadTimeout|NoHostAvailable|OperationTimedOut|Traceback'
}

run_case() {
  state_key=$1
  state_label=$2
  level=$3

  printf '\n=== %s: %s ===\n' "$state_label" "$level"
  printf '$ cqlsh: CONSISTENCY %s; %s\n' "$level" "$READ_CQL"
  if read_output=$(cql "$level" "$READ_CQL"); then read_rc=0; else read_rc=$?; fi
  printf '%s\n' "$read_output"
  if [ "$read_rc" -eq 0 ] && ! has_cql_error "$read_output" && printf '%s\n' "$read_output" | grep -Fq "$READ_ID"; then
    read_result=успех
  else
    read_result=ошибка
    printf '### %s — %s — чтение\n\n```text\n%s\n```\n\n' "$state_label" "$level" "$read_output" >> "$errors"
  fi

  new_id=$(compose exec -T cassandra1 sh -c 'cat /proc/sys/kernel/random/uuid' | tr -d '\r')
  if ! printf '%s\n' "$new_id" | grep -Eq '^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'; then
    printf 'Не удалось получить UUID для новой записи: %s\n' "$new_id" >&2
    exit 1
  fi
  write_cql="INSERT INTO shop_events.service_events (service, event_day, event_time, event_id, error_code, message) VALUES ('checkout', '2026-11-11', '$WRITE_TIME', $new_id, null, 'failover $state_key $level');"
  printf '$ cqlsh: CONSISTENCY %s; %s\n' "$level" "$write_cql"
  if write_output=$(cql "$level" "$write_cql"); then write_rc=0; else write_rc=$?; fi
  printf '%s\n' "$write_output"

  if [ "$write_rc" -eq 0 ] && ! has_cql_error "$write_output"; then
    verify_cql="SELECT event_id, message FROM shop_events.service_events WHERE service = 'checkout' AND event_day = '2026-11-11' AND event_time = '$WRITE_TIME' AND event_id = $new_id;"
    printf '$ cqlsh: CONSISTENCY QUORUM; %s\n' "$verify_cql"
    if verify_output=$(cql QUORUM "$verify_cql"); then verify_rc=0; else verify_rc=$?; fi
    printf '%s\n' "$verify_output"
    if [ "$verify_rc" -eq 0 ] && ! has_cql_error "$verify_output" && printf '%s\n' "$verify_output" | grep -Fq "$new_id"; then
      write_result=успех
    else
      write_result=ошибка
      printf '### %s — %s — проверка записи\n\n```text\n%s\n```\n\n' "$state_label" "$level" "$verify_output" >> "$errors"
    fi
  else
    write_result=ошибка
    printf '### %s — %s — запись\n\n```text\n%s\n```\n\n' "$state_label" "$level" "$write_output" >> "$errors"
  fi

  printf 'Итог: чтение — %s; запись — %s; event_id попытки записи — %s\n' "$read_result" "$write_result" "$new_id"
  printf '| %s | %s | %s | %s |\n' "$state_label" "$level" "$read_result" "$write_result" >> "$matrix"

  if [ "$state_key" = down ] && [ "$level" = ALL ]; then
    expected=ошибка
  else
    expected=успех
  fi
  if [ "$read_result" != "$expected" ] || [ "$write_result" != "$expected" ]; then
    unexpected=$((unexpected + 1))
  fi
}

echo '=== Три узла работают ==='
sh scripts/wait_for_cluster.sh 3 0
run_case initial '3 узла UN' QUORUM
run_case initial '3 узла UN' ALL

echo '=== Остановка cassandra3 ==='
echo '$ docker compose stop cassandra3'
compose stop cassandra3
node_stopped=1
sh scripts/wait_for_cluster.sh 2 1
run_case down '2 UN, 1 DN' QUORUM
run_case down '2 UN, 1 DN' ALL

echo '=== Возврат cassandra3 ==='
echo '$ docker compose start cassandra3'
compose start cassandra3
node_stopped=0
sh scripts/wait_for_cluster.sh 3 0
run_case restored '3 узла UN после возврата' QUORUM
run_case restored '3 узла UN после возврата' ALL

{
  echo '# Результаты проверки отказоустойчивости'
  echo
  echo '| Состояние кластера | Уровень согласованности | Чтение | Запись |'
  echo '|---|---|---|---|'
  cat "$matrix"
  echo
  echo 'При факторе репликации 3 уровень QUORUM требует ответы двух реплик, а ALL — всех трёх. При остановке одного узла QUORUM остаётся доступным, ALL возвращает ошибку. Неуспешная запись с ALL может быть частично применена на работающих репликах, поэтому каждая попытка использует новый event_id.'
  echo
  echo '## Сообщения об ошибках'
  echo
  cat "$errors"
} > results/fault_tolerance.md

echo '=== Таблица результатов ==='
cat results/fault_tolerance.md
if [ "$unexpected" -ne 0 ]; then
  printf 'Неожиданных результатов: %s\n' "$unexpected" >&2
  exit 1
fi
