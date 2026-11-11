#!/usr/bin/env python3
"""Compare two stable from/size pages and verify no repeated video IDs."""

from __future__ import annotations

from query import CATALOG, run


def main() -> None:
    pages = {}
    for name in ("page_1", "page_2"):
        item = next(item for item in CATALOG if item["name"] == name)
        response = run(item)
        pages[name] = [hit["_id"] for hit in response["hits"]["hits"]]
        print()
    overlap = sorted(set(pages["page_1"]) & set(pages["page_2"]))
    print(f"Страница 1: {pages['page_1']}")
    print(f"Страница 2: {pages['page_2']}")
    print(f"Повторяющиеся video_id: {overlap}")
    if overlap or len(pages["page_1"]) != 5 or len(pages["page_2"]) != 5:
        raise SystemExit("Проверка пагинации не пройдена")


if __name__ == "__main__":
    main()
