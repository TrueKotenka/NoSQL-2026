#!/bin/sh
set -eu
. "$(dirname "$0")/common.sh"

echo '$ docker compose ps'
docker compose ps
show PING
show DBSIZE

echo 'Пять типов структур данных'
show TYPE vidlab:stats:views:video:1
show GET vidlab:stats:views:video:1
show TYPE vidlab:video:1
show HGET vidlab:video:1 title
show TYPE vidlab:channel:1:recent
show LRANGE vidlab:channel:1:recent 0 -1
show TYPE vidlab:video:1:tags
show SMEMBERS vidlab:video:1:tags
show TYPE vidlab:videos:rating
show ZRANGE vidlab:videos:rating 0 2 REV WITHSCORES
