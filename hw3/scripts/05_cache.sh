#!/bin/sh
set -eu
. "$(dirname "$0")/common.sh"

key=vidlab:cache:video:1:summary
echo 'Первое обращение: ключ отсутствует'
show DEL "$key"
show EXISTS "$key"
show GET "$key"

title=$(cli HGET vidlab:video:1 title)
views=$(cli GET vidlab:stats:views:video:1)
value=$(printf '{"title":"%s","views":%s}' "$title" "$views")
echo 'Загрузка из основных ключей и сохранение кэша на 120 секунд'
show HGET vidlab:video:1 title
show GET vidlab:stats:views:video:1
show SET "$key" "$value" EX 120

echo 'Повторное обращение: кэш найден'
show GET "$key"
show TTL "$key"
