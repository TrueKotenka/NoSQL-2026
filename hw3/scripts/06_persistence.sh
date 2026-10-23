#!/bin/sh
set -eu
. "$(dirname "$0")/common.sh"

snapshot() {
  printf 'user:1.name=%s\n' "$(cli HGET vidlab:user:1 name)"
  printf 'channel:1.name=%s\n' "$(cli HGET vidlab:channel:1 name)"
  printf 'video:1.title=%s\n' "$(cli HGET vidlab:video:1 title)"
  printf 'video:2.views=%s\n' "$(cli GET vidlab:stats:views:video:2)"
  printf 'video:2.rating=%s\n' "$(cli ZSCORE vidlab:videos:rating video:2)"
}

echo '$ redis-cli CONFIG GET appendonly'
docker compose exec -T redis redis-cli --no-raw CONFIG GET appendonly
echo 'Пять ключей до перезапуска:'
cat <<'COMMANDS'
HGET vidlab:user:1 name
HGET vidlab:channel:1 name
HGET vidlab:video:1 title
GET vidlab:stats:views:video:2
ZSCORE vidlab:videos:rating video:2
COMMANDS
before=$(snapshot)
printf '%s\n' "$before"

echo '$ docker compose restart redis'
docker compose restart redis
attempt=0
until [ "$(cli PING 2>/dev/null || true)" = PONG ]; do
  attempt=$((attempt + 1))
  if [ "$attempt" -ge 30 ]; then echo 'Redis не запустился после перезапуска' >&2; exit 1; fi
  sleep 1
done

echo 'Те же пять ключей после перезапуска:'
cat <<'COMMANDS'
HGET vidlab:user:1 name
HGET vidlab:channel:1 name
HGET vidlab:video:1 title
GET vidlab:stats:views:video:2
ZSCORE vidlab:videos:rating video:2
COMMANDS
after=$(snapshot)
printf '%s\n' "$after"
if [ "$before" = "$after" ]; then
  echo 'Совпадение: да'
else
  echo 'Совпадение: нет' >&2
  exit 1
fi
