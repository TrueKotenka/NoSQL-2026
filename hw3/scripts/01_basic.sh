#!/bin/sh
set -eu
. "$(dirname "$0")/common.sh"

echo 'Создание, получение, изменение, удаление и проверка существования'
show SET vidlab:demo:note 'Посмотреть позже'
show GET vidlab:demo:note
show SET vidlab:demo:note 'Посмотреть сегодня'
show GET vidlab:demo:note
show EXISTS vidlab:demo:note
show HGETALL vidlab:video:1
show MGET vidlab:stats:views:video:1 vidlab:stats:views:video:2
show LRANGE vidlab:channel:1:recent 0 -1
show DEL vidlab:demo:note
show EXISTS vidlab:demo:note
