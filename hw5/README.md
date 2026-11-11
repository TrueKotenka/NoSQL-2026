# Cassandra: журнал событий интернет-магазина

Проект поднимает три узла Cassandra в дата-центре `dc1` и хранит события сервисов `catalog` и `checkout`. Фактор репликации пространства ключей `shop_events` равен 3. Все метки времени и даты в тестовых данных заданы по UTC.

## Состав проекта

| Файл | Назначение |
|---|---|
| `docker-compose.yml` | Три узла Cassandra 4.1.12, отдельные тома и проверка готовности |
| `cql/01_schema.cql` | Пространство ключей, таблица и вторичный индекс |
| `cql/02_seed.cql` | 13 событий двух сервисов за два дня |
| `cql/03_hour.cql` | События `checkout` за интервал `[10:00, 11:00)` |
| `cql/04_error.cql` | Поиск `UPSTREAM_TIMEOUT` по индексу |
| `scripts/setup.sh` | Запуск кластера и загрузка схемы и данных |
| `scripts/queries.sh` | Выполнение двух запросов |
| `scripts/failover.sh` | Проверка чтения и записи при `QUORUM` и `ALL` |
| `results/fault_tolerance.md` | Таблица результатов и сообщения об ошибках после запуска проверки |
| `screenshots/` | PNG и исходные консольные протоколы обязательных проверок |

## Запуск и загрузка данных

Нужны Docker Desktop или Docker Engine с Compose и достаточно памяти для трёх узлов; на машине проверки Docker выделено около 8 ГБ. Из каталога `hw5`:

```bash
sh scripts/setup.sh
docker compose ps
docker compose exec -T cassandra1 nodetool status
```

`setup.sh` ждёт, пока `nodetool status` покажет три строки `UN`, создаёт схему и загружает 13 записей. При повторном запуске CQL использует `IF NOT EXISTS` для схемы и те же первичные ключи для тестовых записей. Тома сохраняют данные после `docker compose down`. Для полного сброса: `docker compose down -v`, затем `sh scripts/setup.sh`.

Подключение к оболочке:

```bash
docker compose exec cassandra1 cqlsh
```

В `cqlsh`:

```sql
SHOW HOST
DESCRIBE KEYSPACE shop_events
DESCRIBE TABLE shop_events.service_events
```

## Модель данных

```sql
CREATE TABLE shop_events.service_events (
    service text,
    event_day date,
    event_time timestamp,
    event_id uuid,
    error_code text,
    message text,
    PRIMARY KEY ((service, event_day), event_time, event_id)
) WITH CLUSTERING ORDER BY (event_time ASC, event_id ASC);
```

| Поле | Тип CQL | Назначение |
|---|---|---|
| `service` | `text` | Сервис, часть ключа партиции |
| `event_day` | `date` | День UTC, часть ключа партиции |
| `event_time` | `timestamp` | Время UTC и первый ключ сортировки |
| `event_id` | `uuid` | Различает события с одинаковым временем |
| `error_code` | `text` | Код ошибки; `null`, если ошибки нет |
| `message` | `text` | Описание события |

Партиция определяется парой `(service, event_day)`. События одной партиции упорядочены по времени, затем по `event_id`. Индекс `service_events_error_code_idx` создан на `error_code`, поэтому запрос по коду не требует ключа партиции и `ALLOW FILTERING`.

В `02_seed.cql` у сервиса `checkout` есть два события в `10:15:00` 10 ноября 2026 года с разными UUID. Код `UPSTREAM_TIMEOUT` встречается у `catalog` и `checkout`.

## Запросы

```bash
sh scripts/queries.sh
```

`03_hour.cql` фиксирует партицию `checkout` за 10 ноября 2026 года и выбирает времена от `10:00` включительно до `11:00` исключительно. Ожидаются три строки: две в `10:15` и одна в `10:45`. Строки в `09:59` и `11:00` исключены. `ORDER BY event_time ASC` сохраняет порядок по времени.

`04_error.cql` выбирает `UPSTREAM_TIMEOUT` только по `error_code`. Ожидаются три строки: две от `catalog` и одна от `checkout`. В запросе отсутствуют `service`, `event_day` и `ALLOW FILTERING`.

## Проверка отказоустойчивости

После загрузки данных:

```bash
sh scripts/failover.sh > results/fault_test.log 2>&1
cat results/fault_tolerance.md
```

Скрипт читает заранее загруженную строку `checkout` с UUID `00000000-0000-4000-8000-000000000008` по полному первичному ключу. Для каждой записи он получает новый UUID из работающего контейнера. Проверяются шесть сочетаний: три состояния кластера × `QUORUM` и `ALL`. После остановки `cassandra3` скрипт ждёт `2 UN, 1 DN`, а после запуска — `3 UN`. Он автоматически запускает остановленный узел при прерывании.

При факторе репликации 3 `QUORUM` требует ответы двух реплик, `ALL` — трёх. Ожидаемая матрица:

| Состояние кластера | Уровень | Чтение | Запись |
|---|---|---|---|
| 3 `UN` до остановки | `QUORUM`, `ALL` | Успех | Успех |
| 2 `UN`, 1 `DN` | `QUORUM` | Успех | Успех |
| 2 `UN`, 1 `DN` | `ALL` | Ошибка | Ошибка |
| 3 `UN` после возврата | `QUORUM`, `ALL` | Успех | Успех |

Фактическая таблица и тексты ошибок записываются в `results/fault_tolerance.md`; полные команды и ответы находятся в `results/fault_test.log`. Ошибка записи с `ALL` не означает откат уже получивших её реплик, поэтому каждая попытка использует отдельный `event_id`.

## Скриншоты и протоколы

После `setup.sh`:

```bash
sh scripts/capture_static.sh
sh scripts/failover.sh > results/fault_test.log 2>&1
sh scripts/split_failover.sh
```

Исходные `.log` содержат фактический вывод и остаются в архиве.

| Файл | Содержание |
|---|---|
| `01_cluster.png` | `docker compose ps`, `nodetool status`, три `UN` |
| `02_schema.png` | Подключение через `cqlsh`, `DESCRIBE TABLE`, первичный ключ и индекс |
| `03_hour.png` | Запрос за час и три строки результата |
| `04_error.png` | Поиск по коду ошибки и оба сервиса |
| `05_down.png` | `2 UN, 1 DN`, `QUORUM` и `ALL`, ошибки чтения и записи |
| `06_restored.png` | Возврат к `3 UN` и успешная проверка `ALL` |

Каждый PNG построен из сохранённого консольного протокола; команды и ответы показаны вместе.

## Остановка

```bash
docker compose down
```
