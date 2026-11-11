#!/bin/sh
set -eu
. "$(dirname "$0")/common.sh"

input=results/fault_test.log
if [ ! -s "$input" ]; then
  echo "Нет файла $input. Выполните sh scripts/failover.sh > $input 2>&1" >&2
  exit 1
fi

awk '/^=== Остановка cassandra3 ===/{copy=1} /^=== Возврат cassandra3 ===/{copy=0} copy' "$input" > screenshots/05_down.log
awk '/^=== Возврат cassandra3 ===/{copy=1} /^=== Таблица результатов ===/{copy=0} copy' "$input" > screenshots/06_restored.log

test -s screenshots/05_down.log
test -s screenshots/06_restored.log
echo 'Протоколы отказа и восстановления сохранены в screenshots/05–06_*.log'
