# Лабораторная работа 3 — Redis для видеосервиса

Учебный видеосервис хранит пользователей, каналы, видео, историю просмотров, подписки, рейтинг и кратковременный кэш. Все ключи имеют префикс `vidlab:`. Связи между объектами представлены идентификаторами вида `user:1`, `channel:1`, `video:1` в значениях структур Redis.

## Файлы

| Файл | Назначение |
|---|---|
| `docker-compose.yml` | Redis и однократный загрузчик данных |
| `redis.conf` | AOF с `appendfsync everysec`; каталог `/data` |
| `scripts/seed.sh` | Автоматическое начальное заполнение |
| `scripts/00_status.sh` | Состояние контейнера, подключение и пять типов ключей |
| `scripts/01_basic.sh` | Основные операции с ключами |
| `scripts/02_ttl_counter.sh` | TTL и атомарный счётчик |
| `scripts/03_collections.sh` | List, Set, Sorted Set |
| `scripts/04_transaction.sh` | `MULTI` / `EXEC` |
| `scripts/05_cache.sh` | Чтение через кэш с TTL |
| `scripts/06_persistence.sh` | Проверка пяти ключей до и после перезапуска Redis |
| `scripts/07_memory.sh` | `TYPE` и `MEMORY USAGE` для трёх типов |
| `scripts/run_all.sh` | Последовательный запуск демонстраций |
| `scripts/capture_logs.sh` | Запись фактического вывода команд для иллюстраций |

## Запуск

Из каталога `hw3`:

```bash
docker compose up -d
docker compose ps
docker compose logs seed
docker compose exec redis redis-cli PING
docker compose exec redis redis-cli DBSIZE
```

Контейнер `seed` ждёт готовности Redis, запускает `seed.sh` и завершается. Скрипт создаёт **29 ключей** при пустом томе. Маркер `vidlab:meta:seeded` предотвращает повторную загрузку при следующем `docker compose up -d`; изменения и проверка AOF после перезапуска сохраняются. Redis доступен локально на `127.0.0.1:6379`. Для полного сброса учебного тома: `docker compose down -v`, затем `docker compose up -d`. Команда `down` без `-v` данные сохраняет.

Подключение к клиенту:

```bash
docker compose exec redis redis-cli
```

В интерактивном клиенте:

```text
PING
TYPE vidlab:user:1
HGETALL vidlab:user:1
QUIT
```

## Схема ключей

| Шаблон и пример | Тип | Назначение | Количество при загрузке |
|---|---|---|---:|
| `vidlab:user:{id}` | Hash | Имя, город, тариф пользователя | 4 |
| `vidlab:channel:{id}` | Hash | Канал и идентификатор владельца | 3 |
| `vidlab:video:{id}` | Hash | Видео, канал, категория, лайки | 6 |
| `vidlab:stats:views:video:{id}` | String | Числовой счётчик просмотров | 4 |
| `vidlab:channel:{id}:recent`, `vidlab:user:{id}:history` | List | Последние видео канала и история пользователя | 3 |
| `vidlab:video:{id}:tags`, `vidlab:channel:{id}:subscribers`, `vidlab:user:{id}:subscriptions` | Set | Теги и подписки без повторов | 4 |
| `vidlab:videos:rating`, `vidlab:channel:{id}:popular` | Sorted Set | Рейтинг видео по баллам | 2 |
| `vidlab:session:user:{id}`, `vidlab:token:reset:user:{id}` | String + TTL | Сессия и одноразовый токен | 2 |
| `vidlab:meta:seeded` | String | Маркер загрузки | 1 |

После запуска демонстрационных скриптов могут появиться дополнительные ключи `vidlab:demo:*` и `vidlab:cache:*`. Временные ключи удаляются или истекают по TTL. Число 29 относится к первичной загрузке до демонстраций.

## Основные операции

```bash
sh scripts/01_basic.sh
```

Скрипт показывает `SET`, `GET`, повторный `SET` для обновления, `DEL`, `EXISTS`, `HGETALL`, `MGET` и `LRANGE`. Временная заметка `vidlab:demo:note` удаляется в конце. Основные данные остаются доступными. Примеры числовых значений возвращает `MGET` счётчиков просмотров.

## TTL и счётчик

```bash
sh scripts/02_ttl_counter.sh
```

Скрипт создаёт два ключа с `EX 120` и `EX 180`, проверяет оба через `TTL`, продлевает сессию командой `EXPIRE ... 300`, снимает ограничение второго ключа через `PERSIST` и повторно проверяет `TTL`. После `PERSIST` ответ `-1` означает существующий ключ без срока жизни; `-2` означал бы отсутствующий ключ.

Счётчик `vidlab:stats:views:video:1` устанавливается в `100`, затем три атомарные операции дают последовательность `101` (`INCR`), `106` (`INCRBY 5`), `104` (`DECRBY 2`). Итог проверяется через `GET`.

## List, Set и Sorted Set

```bash
sh scripts/03_collections.sh
```

| Тип | Операции сверх добавления |
|---|---|
| List | `LRANGE 0 -1` — весь список; `LINDEX -1` — последний элемент; `LPOS` — позиция видео |
| Set | `SMEMBERS` — все элементы; `SISMEMBER` — принадлежность; `SCARD` — число элементов |
| Sorted Set | `ZRANGE ... REV WITHSCORES` — рейтинг; `ZREVRANK` — место; `ZSCORE` — балл видео |

## Транзакция

```bash
sh scripts/04_transaction.sh
```

Перед транзакцией скрипт задаёт баланс `100`, число оплаченных просмотров `0` и пустой набор доступа. Один сеанс `redis-cli` выполняет:

```text
MULTI
DECRBY vidlab:demo:balance:user:1 10
INCRBY vidlab:demo:paid_views:video:1 1
SADD vidlab:demo:access:user:1 video:1
EXEC
```

До `EXEC` три изменения находятся в очереди (`QUEUED`). Ответ `EXEC` содержит результаты `90`, `1`, `1`. После транзакции баланс равен `90`, оплаченных просмотров `1`, набор доступа содержит `video:1`. Состояние до и после и ответ `EXEC` печатаются скриптом.

## Кэширование

```bash
sh scripts/05_cache.sh
```

Первое обращение к `vidlab:cache:video:1:summary` даёт отсутствие ключа. Скрипт получает название из Hash и число просмотров из String, сохраняет JSON-строку командой `SET ... EX 120`. Повторный `GET` возвращает сохранённое значение, `TTL` показывает остаток срока жизни. Скрипт удаляет прежнее значение кэша в начале, поэтому повторяется с теми же шагами.

## Сохранение данных

В `redis.conf` включён AOF: `appendonly yes`, `appendfsync everysec`. Каталог `/data` подключён к именованному тому `redis_data`. Скрипт проверяет наличие AOF и пять постоянных ключей до и после перезапуска контейнера:

```bash
sh scripts/06_persistence.sh
```

Проверяются `vidlab:user:1`, `vidlab:channel:1`, `vidlab:video:1`, `vidlab:stats:views:video:2`, `vidlab:videos:rating`. В конце выводится `Совпадение: да`, если значения до и после перезапуска идентичны. Ключи с TTL в это сравнение не входят.

## Анализ памяти

```bash
sh scripts/07_memory.sh
```

Скрипт строит таблицу по ключам разных типов. Показатели в байтах получаются непосредственно через `MEMORY USAGE ... SAMPLES 0` и зависят от версии Redis и фактического размещения в памяти.

| Ключ | Ожидаемый TYPE | MEMORY USAGE, байт |
|---|---|---:|
| `vidlab:user:1` | hash | 120 |
| `vidlab:channel:1:recent` | list | 112 |
| `vidlab:videos:rating` | zset | 144 |

## Повторение всех проверок

```bash
sh scripts/00_status.sh
sh scripts/run_all.sh
```

Скрипты печатают команду перед ответом Redis. В `scripts/04_transaction.sh` команды `MULTI` и `EXEC` передаются одному соединению, поэтому транзакция действительно выполняется. `scripts/06_persistence.sh` вызывает `docker compose restart redis`, сохраняет значения пяти ключей до и после и сравнивает их.

## Скриншоты

| Файл в `screenshots/` | Что должно быть видно |
|---|---|
| `01_container.png` | `docker compose ps`, запущенный контейнер Redis |
| `02_connection.png` | `redis-cli PING` и `PONG` |
| `03_structures.png` | `TYPE`/чтение String, Hash, List, Set, Sorted Set |
| `04_ttl_counter.png` | `TTL`, `EXPIRE`, `PERSIST`, три изменения счётчика |
| `05_collections.png` | Диапазон List, элементы Set, рейтинг Sorted Set |
| `06_transaction.png` | Состояние до, `MULTI`, `QUEUED`, `EXEC`, состояние после |
| `07_cache.png` | Промах, `SET ... EX`, попадание, `TTL` |
| `08_persistence.png` | Пять значений до и после `docker compose restart redis` |
| `09_memory.png` | Таблица `TYPE` и `MEMORY USAGE` для трёх ключей |
| `10_basic.png` | Создание, получение, изменение, удаление и проверка ключа |

В каждом PNG видны команда и соответствующий результат. Для разделов с несколькими действиями вывод сохранён целиком.

Файлы `screenshots/*.log` содержат исходный консольный вывод. Его можно повторно получить командой `sh scripts/capture_logs.sh` после запуска Redis.
