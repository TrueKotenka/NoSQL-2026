#!/bin/sh
set -eu
. "$(dirname "$0")/common.sh"

echo 'Два ключа с TTL, изменение TTL и удаление ограничения'
show SET vidlab:session:user:1 session-anna EX 120
show SET vidlab:token:reset:user:2 reset-boris EX 180
show TTL vidlab:session:user:1
show TTL vidlab:token:reset:user:2
show EXPIRE vidlab:session:user:1 300
show TTL vidlab:session:user:1
show PERSIST vidlab:token:reset:user:2
show TTL vidlab:token:reset:user:2

echo 'Атомарный счётчик просмотров: 100 → 101 → 106 → 104'
show SET vidlab:stats:views:video:1 100
show INCR vidlab:stats:views:video:1
show INCRBY vidlab:stats:views:video:1 5
show DECRBY vidlab:stats:views:video:1 2
show GET vidlab:stats:views:video:1
