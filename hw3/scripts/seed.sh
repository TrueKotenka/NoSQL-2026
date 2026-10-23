#!/bin/sh
set -eu

cli() { redis-cli -h "${REDIS_HOST:-redis}" --raw "$@"; }

# Маркер хранится в томе вместе с данными: повторный compose up не перезаписывает
# результаты демонстраций и не мешает проверке сохранения после перезапуска.
if [ "$(cli EXISTS vidlab:meta:seeded)" = 1 ]; then
  echo 'Демонстрационные данные уже загружены.'
  exit 0
fi

cli HSET vidlab:user:1 name Анна city Москва plan premium >/dev/null
cli HSET vidlab:user:2 name Борис city Казань plan free >/dev/null
cli HSET vidlab:user:3 name Вера city Минск plan free >/dev/null
cli HSET vidlab:user:4 name Глеб city Алматы plan premium >/dev/null

cli HSET vidlab:channel:1 name 'Код и кофе' owner_id 1 category Технологии >/dev/null
cli HSET vidlab:channel:2 name 'Физика рядом' owner_id 2 category Наука >/dev/null
cli HSET vidlab:channel:3 name 'Город пешком' owner_id 3 category Путешествия >/dev/null

cli HSET vidlab:video:1 title 'Индексы в MongoDB' channel_id 1 category Технологии likes 36 >/dev/null
cli HSET vidlab:video:2 title 'Как устроены базы данных' channel_id 1 category Технологии likes 42 >/dev/null
cli HSET vidlab:video:3 title 'Почему небо голубое' channel_id 2 category Наука likes 25 >/dev/null
cli HSET vidlab:video:4 title 'Выходные в Казани' channel_id 3 category Путешествия likes 31 >/dev/null
cli HSET vidlab:video:5 title 'Что такое кэширование' channel_id 1 category Технологии likes 28 >/dev/null
cli HSET vidlab:video:6 title 'Наблюдаем звёзды' channel_id 2 category Наука likes 38 >/dev/null

cli SET vidlab:stats:views:video:1 100 >/dev/null
cli SET vidlab:stats:views:video:2 245 >/dev/null
cli SET vidlab:stats:views:video:3 185 >/dev/null
cli SET vidlab:stats:views:video:4 210 >/dev/null

cli RPUSH vidlab:channel:1:recent video:2 video:5 video:1 >/dev/null
cli RPUSH vidlab:user:1:history video:3 video:2 video:1 >/dev/null
cli RPUSH vidlab:channel:2:recent video:3 video:6 >/dev/null

cli SADD vidlab:video:1:tags mongodb redis databases >/dev/null
cli SADD vidlab:channel:1:subscribers user:1 user:2 user:3 >/dev/null
cli SADD vidlab:user:1:subscriptions channel:1 channel:2 >/dev/null
cli SADD vidlab:video:3:tags science physics >/dev/null

cli ZADD vidlab:videos:rating 36 video:1 42 video:2 25 video:3 31 video:4 28 video:5 38 video:6 >/dev/null
cli ZADD vidlab:channel:1:popular 100 video:1 245 video:2 80 video:5 >/dev/null

cli SET vidlab:session:user:1 'session-anna' EX 3600 >/dev/null
cli SET vidlab:token:reset:user:2 'reset-boris' EX 1800 >/dev/null
cli SET vidlab:meta:seeded 1 >/dev/null

echo 'Загружены демонстрационные данные.'
echo "Ключей с префиксом vidlab: $(cli --scan --pattern 'vidlab:*' | wc -l | tr -d ' ')"
