#!/usr/bin/env python3
"""Run named search bodies from queries/catalog.json and print request plus result."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from es_client import compact_hits, pretty, request


ROOT = Path(__file__).resolve().parent.parent
CATALOG = json.loads((ROOT / "queries" / "catalog.json").read_text(encoding="utf-8"))


def run(item: dict) -> dict:
    name = item["name"]
    print(f"$ python3 scripts/query.py {name}")
    print("POST /videos/_search")
    print(pretty(item["body"]))
    response = request("POST", "/videos/_search", item["body"])
    summary = compact_hits(response)
    print("RESULT")
    print(f"total={summary['total']}")
    for position, hit in enumerate(summary["hits"], start=1):
        score = "null" if hit["score"] is None else f"{hit['score']:.5f}"
        print(f"{position}. {hit['id']} score={score} views={hit['views']} category={hit['category']} title={hit['title']}")
        if "highlight" in hit:
            print(f"   highlight={json.dumps(hit['highlight'], ensure_ascii=False)}")
    if "aggregations" in summary:
        print(pretty(summary["aggregations"]))
    print(f"Ожидание: {item['expect']}")
    return response


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("name", nargs="?", help="имя запроса из каталога")
    parser.add_argument("--group", help="выполнить все запросы выбранной группы")
    parser.add_argument("--list", action="store_true", help="показать доступные имена")
    args = parser.parse_args()

    if args.list:
        for item in CATALOG:
            print(f"{item['group']:14} {item['name']}")
        return
    selected = [item for item in CATALOG if item["name"] == args.name] if args.name else []
    if args.group:
        selected = [item for item in CATALOG if item["group"] == args.group or args.group == "all"]
    if not selected:
        parser.error("укажите существующее имя запроса или --group")
    for index, item in enumerate(selected):
        if index:
            print("\n" + "=" * 80 + "\n")
        run(item)


if __name__ == "__main__":
    main()
