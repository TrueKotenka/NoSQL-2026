#!/usr/bin/env python3
"""Create the videos index and bulk-load deterministic demonstration data."""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

from es_client import ApiError, pretty, request


ROOT = Path(__file__).resolve().parent.parent
INDEX = "videos"


def wait_for_elasticsearch() -> None:
    for attempt in range(90):
        try:
            response = request("GET", "/")
            print(f"Elasticsearch доступен: {response['version']['number']}")
            return
        except Exception:
            time.sleep(2)
    raise RuntimeError("Elasticsearch не ответил за 180 секунд")


def load(reset: bool) -> None:
    wait_for_elasticsearch()
    documents = json.loads((ROOT / "data" / "videos.json").read_text(encoding="utf-8"))
    if len(documents) < 30 or len({doc["video_id"] for doc in documents}) != len(documents):
        raise ValueError("Нужны минимум 30 документов с уникальными video_id")

    if reset:
        try:
            request("DELETE", f"/{INDEX}")
            print(f"Удалён индекс {INDEX} для повторной загрузки")
        except ApiError as exc:
            if exc.status != 404:
                raise

    try:
        request("GET", f"/{INDEX}")
    except ApiError as exc:
        if exc.status != 404:
            raise
        mapping = json.loads((ROOT / "mapping.json").read_text(encoding="utf-8"))
        response = request("PUT", f"/{INDEX}", mapping)
        print(f"Создан индекс {INDEX}: acknowledged={response['acknowledged']}")

    count = request("GET", f"/{INDEX}/_count")["count"]
    if count != 0:
        print(f"Индекс уже содержит {count} документов; данные сохранены без перезаписи. Для исходных 36: --reset")
        return

    lines = []
    for document in documents:
        lines.append(json.dumps({"index": {"_index": INDEX, "_id": document["video_id"]}}, ensure_ascii=False))
        lines.append(json.dumps(document, ensure_ascii=False))
    response = request("POST", "/_bulk?refresh=wait_for", "\n".join(lines) + "\n", ndjson=True)
    if response["errors"]:
        failures = [item for item in response["items"] if item["index"]["status"] >= 400]
        raise RuntimeError(f"Ошибки Bulk API:\n{pretty(failures[:3])}")
    final = request("GET", f"/{INDEX}/_count")["count"]
    print(f"Bulk API: загружено {final} документов")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--reset", action="store_true", help="удалить индекс и загрузить данные заново")
    args = parser.parse_args()
    load(args.reset)
