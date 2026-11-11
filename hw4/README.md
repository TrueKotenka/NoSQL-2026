# Лабораторная работа 4 — поиск видео в Elasticsearch

Учебный видеосервис ищет ролики по названию и описанию, отбирает их по категории, просмотрам и наличию субтитров, сортирует выдачу и строит статистику публикаций. Основной индекс — `videos`; исходный набор содержит **36 роликов** в шести категориях. Каждый документ имеет отдельный `video_id` (`v001`–`v036`), который используется как `_id` в Elasticsearch.

## Состав проекта

| Путь | Назначение |
|---|---|
| `docker-compose.yml` | Elasticsearch 8.15.0 и автоматический загрузчик `seed` |
| `mapping.json` | Явный mapping индекса `videos` |
| `data/videos.json` | 36 демонстрационных документов |
| `scripts/build_data.py` | Воспроизведение исходного JSON из фиксированного каталога |
| `scripts/load.py` | Создание индекса и загрузка через Bulk API |
| `queries/catalog.json` | Тела запросов и ожидаемые результаты |
| `scripts/query.py` | Выполнение именованных REST-запросов |
| `scripts/check_pagination.py` | Сравнение двух страниц |
| `scripts/compare_scores.py` | Сравнение рангов и `_score` при разных boost |
| `scripts/mutations.py` | Поиск, Update API, Delete API и повторный поиск |
| `scripts/capture_evidence.py` | Запись фактических запросов и ответов в `.log` |
| `screenshots/` | Протоколы команд и иллюстрации результатов |

## Запуск

Требуются Docker Desktop или Docker Engine с Compose. Для запуска запросов с хоста нужен Python 3 без сторонних библиотек.

```bash
cd hw4
docker compose up -d
docker compose ps
docker compose logs seed
curl -s http://127.0.0.1:9200/
curl -s http://127.0.0.1:9200/videos/_count
```

Elasticsearch слушает только `127.0.0.1:9200`; авторизация отключена в локальном учебном контейнере. Сервис `seed` ждёт готовности Elasticsearch, создаёт индекс по `mapping.json`, загружает документы через Bulk API и завершается с кодом `0`. На пустом томе `_count` возвращает `36`. Повторный `docker compose up -d` не перезаписывает существующие документы. Для восстановления исходных 36 документов после демонстрации обновления и удаления:

```bash
python3 scripts/load.py --reset
```

Команда полного удаления локального тома: `docker compose down -v`. Обычный `docker compose down` сохраняет данные в именованном томе `elasticsearch_data`.

## Документ и mapping

| Поле | Тип | Назначение |
|---|---|---|
| `video_id` | `keyword` | Устойчивый идентификатор, точный поиск и сортировка при равенстве основных полей |
| `title` | `text` | Полнотекстовый поиск по названию |
| `description` | `text` | Полнотекстовый поиск по описанию |
| `category` | `keyword` | Точная фильтрация и агрегация по категориям |
| `channel` | `keyword` | Название канала |
| `tags` | `keyword` | Массив точных тегов |
| `views` | `integer` | Диапазоны, сортировка, среднее значение |
| `rating` | `float` | Числовой рейтинг |
| `published_at` | `date` | Сортировка и группировка по месяцам |
| `is_premium` | `boolean` | Фильтр по доступности |
| `duration_minutes` | `integer` | Длительность |
| `subtitles` | `keyword` | Необязательное поле для проверки `exists` |

Поля `title` и `description` анализируются стандартным анализатором Elasticsearch. `dynamic: strict` запрещает загрузку неизвестных полей. Один shard и ноль реплик выбраны для одиночного учебного узла. Проверка структуры и количества:

```bash
curl -s http://127.0.0.1:9200/videos/_mapping
curl -s http://127.0.0.1:9200/videos/_count
```

## Поисковые запросы

Полные тела REST-запросов находятся в `queries/catalog.json`. Клиент печатает метод, путь, тело запроса, общее число совпадений и найденные ролики. Примеры:

```bash
python3 scripts/query.py --list
python3 scripts/query.py match
python3 scripts/query.py --group basic
python3 scripts/query.py --group bool
python3 scripts/query.py --group aggregations
python3 scripts/query.py --group all
```

| Запрос | Условие | Результат исходного набора и причина |
|---|---|---|
| `match` | `title: Redis` | `v001`, `v002`: слово есть в названиях |
| `match_phrase` | `title: «базы данных»` | `v003`, `v006`: слова идут подряд в том же порядке |
| `multi_match` | `Redis` в `title` или `description` | `v001`, `v002`, `v003`: у `v003` слово есть только в описании |
| `term` | `category = technology` | 6 роликов: `keyword` сравнивается точно |
| `range` | `10000 <= views < 15000` | 12 роликов: верхняя граница не включена |
| `exists` | поле `subtitles` присутствует | 12 роликов из 36: поле есть у каждого третьего документа |

## Составные запросы и фильтр

| Запрос | Условия | Найдено |
|---|---|---:|
| `bool_must_filter` | `must`: Redis в описании; `filter`: категория `technology`, `views >= 5000` | 2 (`v002`, `v003`) |
| `bool_should` | Бесплатный ролик; Redis в заголовке **или** теге, `minimum_should_match: 1` | 3 |
| `bool_must_not` | `must`: данные в заголовке; `must_not`: категория `technology` | 2 (`v008`, `v016`) |
| `compare_unfiltered` | Данные в названии или описании, все категории | 4 |
| `compare_filtered` | Тот же полнотекстовый поиск и `filter` по `technology` | 1 (`v003`) |

Фильтр уменьшает выдачу с четырёх роликов до одного без изменения текстового условия. Все три основных `bool`-запроса содержат минимум два условия.

## Сортировка и пагинация

`sort_views_asc` выдаёт сначала `v014` (3306 просмотров), а `sort_views_desc` — `v027` (21233). `sort_score` сортирует совпадения Redis по убыванию `_score`. При сортировке по обычным полям Elasticsearch не вычисляет `_score` для вывода, поэтому в строках этих запросов он показан как `null`.

`page_1` и `page_2` используют одинаковую сортировку `published_at desc`, затем `video_id asc`, и параметры `from: 0/5`, `size: 5`. Проверка:

```bash
python3 scripts/query.py sort_views_asc
python3 scripts/query.py sort_views_desc
python3 scripts/query.py sort_score
python3 scripts/check_pagination.py
```

Первая страница: `v036`–`v032`; вторая: `v031`–`v027`. Пересечение идентификаторов пусто (`[]`). Поле `video_id` завершает сортировку и обеспечивает устойчивый порядок.

## Релевантность

В `compare_scores.py` один и тот же запрос `Redis` выполняется двумя способами: с `description^2` и с `title^3`. В обоих случаях это `multi_match`; различаются только веса полей.

| Видео | `description^2`: место, `_score` | `title^3`: место, `_score` |
|---|---:|---:|
| `v001` | 2, 4.15035 | 1, 8.37420 |
| `v002` | 1, 4.38418 | 2, 8.37420 |
| `v003` | 3, 4.15035 | 3, 2.07518 |

При усилении заголовка `v001` поднимается на первое место, а `v003`, где Redis есть только в описании, получает меньший `_score`. Дополнительно `fuzziness: AUTO` находит `Kubernetes` по запросу с опечаткой `Kubernets`; `highlight` выделяет совпадения Redis в названии и описании тегами `<mark>`.

```bash
python3 scripts/compare_scores.py
python3 scripts/query.py fuzziness
python3 scripts/query.py highlight
```

## Агрегации

| Запрос | Результат | Смысл |
|---|---|---|
| `agg_terms` | 6 категорий по 6 роликов | Распределение документов по `category` |
| `agg_avg_filtered` | `8227.3333` просмотров | Среднее только для 6 роликов `technology`, отобранных через `query` |
| `agg_date_histogram` | Январь 10, февраль 9, март 11, апрель 6 | Число публикаций по месяцам `published_at` |

```bash
python3 scripts/query.py --group aggregations
```

## Обновление и удаление

```bash
python3 scripts/mutations.py update
python3 scripts/mutations.py delete
python3 scripts/load.py --reset
```

Сценарий `update` находит `v005` по полю `video_id` и показывает `views = 12300`. Запрос с порогом `views >= 20000` возвращает `0` документов. Update API меняет `views` на `24000` с `refresh=wait_for`; тот же запрос затем возвращает `v005`. Сценарий `delete` находит `v036`, удаляет его через Delete API с `refresh=wait_for` и повторным поиском подтверждает `total=0`. Каждый сценарий восстанавливает исходное состояние своего тестового документа перед действиями, поэтому команды можно повторять. `load.py --reset` полностью возвращает исходный индекс.

## Результаты выполнения

Файлы `screenshots/*.log` содержат фактические запросы и ответы Elasticsearch. PNG построены из этих протоколов, поэтому в каждом изображении одновременно видны запрос и результат. Для повторной записи и построения PNG на macOS:

```bash
python3 scripts/load.py --reset
python3 scripts/capture_evidence.py
python3 scripts/load.py --reset
```

`capture_evidence.py` последними выполняет обновление и удаление; завершающая загрузка возвращает исходные 36 документов.

| PNG | Содержание |
|---|---|
| `01_container`–`03_mapping_count` | Контейнер, REST API, mapping и число документов |
| `04_match`–`09_exists` | Шесть основных типов запросов |
| `10_bool_must_filter`–`13_filter_comparison` | Составные условия и сравнение фильтрации |
| `14_sort_asc_desc`–`16_pagination` | Сортировка по просмотрам, `_score` и две страницы без повторов |
| `17_score_comparison`–`19_highlight` | Boost, сравнение `_score`, fuzziness и highlight |
| `20_agg_terms`–`22_agg_date_histogram` | Три агрегации |
| `23_update`, `24_delete` | Изменение и удаление с поиском до и после |

Все указанные имена имеют расширение `.png`; рядом лежит одноимённый `.log`. После распаковки достаточно `docker compose up -d`: контейнер `seed` создаст индекс и загрузит данные автоматически.
