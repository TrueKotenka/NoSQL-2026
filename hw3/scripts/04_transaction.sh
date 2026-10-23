#!/bin/sh
set -eu
. "$(dirname "$0")/common.sh"

# Подготовка делает демонстрацию повторяемой.
cli SET vidlab:demo:balance:user:1 100 >/dev/null
cli SET vidlab:demo:paid_views:video:1 0 >/dev/null
cli DEL vidlab:demo:access:user:1 >/dev/null

echo 'До транзакции'
show GET vidlab:demo:balance:user:1
show GET vidlab:demo:paid_views:video:1
show SMEMBERS vidlab:demo:access:user:1

echo 'Один клиент Redis, три операции изменения между MULTI и EXEC:'
cat <<'COMMANDS'
MULTI
DECRBY vidlab:demo:balance:user:1 10
INCRBY vidlab:demo:paid_views:video:1 1
SADD vidlab:demo:access:user:1 video:1
EXEC
COMMANDS

docker compose exec -T redis redis-cli --no-raw <<'COMMANDS'
MULTI
DECRBY vidlab:demo:balance:user:1 10
INCRBY vidlab:demo:paid_views:video:1 1
SADD vidlab:demo:access:user:1 video:1
EXEC
COMMANDS

echo 'После транзакции'
show GET vidlab:demo:balance:user:1
show GET vidlab:demo:paid_views:video:1
show SMEMBERS vidlab:demo:access:user:1
