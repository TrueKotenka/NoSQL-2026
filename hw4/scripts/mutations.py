#!/usr/bin/env python3
"""Show Update API visibility and deletion with a repeatable baseline."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from es_client import request


ROOT = Path(__file__).resolve().parent.parent
DOCUMENTS = {doc["video_id"]: doc for doc in json.loads((ROOT / "data" / "videos.json").read_text(encoding="utf-8"))}


def search(body: dict) -> dict:
    print("POST /videos/_search")
    print(json.dumps(body, ensure_ascii=False, separators=(",", ":")))
    response = request("POST", "/videos/_search", body)
    hits = response["hits"]["hits"]
    print(f"total={response['hits']['total']['value']}")
    for hit in hits:
        print(f"{hit['_id']}: title={hit['_source']['title']}; views={hit['_source']['views']}")
    return response


def update_demo() -> None:
    print("Подготовка исходного состояния для v005")
    print("PUT /videos/_doc/v005?refresh=wait_for")
    restored = request("PUT", "/videos/_doc/v005?refresh=wait_for", DOCUMENTS["v005"])
    print(f"result={restored['result']}; _id={restored['_id']}")

    target = {"query": {"term": {"video_id": "v005"}}, "size": 1, "track_total_hits": True}
    threshold = {
        "query": {"bool": {"filter": [{"term": {"video_id": "v005"}}, {"range": {"views": {"gte": 20000}}}]}},
        "size": 5,
        "track_total_hits": True,
    }
    print("\nПоиск документа по полю video_id до обновления")
    search(target)
    print("\nПоиск по порогу views >= 20000 до обновления")
    search(threshold)
    print("\nPOST /videos/_update/v005?refresh=wait_for")
    print('{"doc":{"views":24000}}')
    updated = request("POST", "/videos/_update/v005?refresh=wait_for", {"doc": {"views": 24000}})
    print(f"result={updated['result']}; _id={updated['_id']}")
    print("\nТот же поиск по порогу после обновления")
    search(threshold)


def delete_demo() -> None:
    print("Подготовка исходного состояния для v036")
    print("PUT /videos/_doc/v036?refresh=wait_for")
    restored = request("PUT", "/videos/_doc/v036?refresh=wait_for", DOCUMENTS["v036"])
    print(f"result={restored['result']}; _id={restored['_id']}")
    deleted = {"query": {"term": {"video_id": "v036"}}, "size": 5, "track_total_hits": True}
    print("\nПоиск тестового документа до удаления")
    search(deleted)
    print("\nDELETE /videos/_doc/v036?refresh=wait_for")
    deleted_response = request("DELETE", "/videos/_doc/v036?refresh=wait_for")
    print(f"result={deleted_response['result']}; _id={deleted_response['_id']}")
    print("\nТот же поиск после удаления")
    search(deleted)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("part", choices=("update", "delete", "all"), nargs="?", default="all")
    part = parser.parse_args().part
    if part in ("update", "all"):
        update_demo()
    if part == "all":
        print("\n" + "=" * 80 + "\n")
    if part in ("delete", "all"):
        delete_demo()


if __name__ == "__main__":
    main()
