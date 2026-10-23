#!/bin/sh
set -eu
. "$(dirname "$0")/common.sh"

echo 'List: диапазон, последний элемент и позиция'
show LRANGE vidlab:channel:1:recent 0 -1
show LINDEX vidlab:channel:1:recent -1
show LPOS vidlab:channel:1:recent video:5

echo 'Set: элементы, принадлежность и размер'
show SMEMBERS vidlab:video:1:tags
show SISMEMBER vidlab:video:1:tags redis
show SCARD vidlab:video:1:tags

echo 'Sorted Set: рейтинг, место и балл элемента'
show ZRANGE vidlab:videos:rating 0 -1 REV WITHSCORES
show ZREVRANK vidlab:videos:rating video:2
show ZSCORE vidlab:videos:rating video:2
