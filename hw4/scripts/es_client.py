#!/usr/bin/env python3
"""Small standard-library REST client used by the lab scripts."""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from typing import Any


BASE_URL = os.environ.get("ELASTICSEARCH_URL", "http://127.0.0.1:9200").rstrip("/")


class ApiError(RuntimeError):
    def __init__(self, status: int, body: str):
        self.status = status
        self.body = body
        super().__init__(f"HTTP {status}: {body}")


def request(method: str, path: str, body: Any = None, *, ndjson: bool = False) -> Any:
    data = None
    headers = {}
    if body is not None:
        data = body.encode("utf-8") if ndjson else json.dumps(body, ensure_ascii=False).encode("utf-8")
        headers["Content-Type"] = "application/x-ndjson" if ndjson else "application/json"
    req = urllib.request.Request(BASE_URL + path, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=60) as response:
            raw = response.read().decode("utf-8")
            return json.loads(raw) if raw else None
    except urllib.error.HTTPError as exc:
        raise ApiError(exc.code, exc.read().decode("utf-8")) from exc


def compact_hits(response: dict[str, Any]) -> dict[str, Any]:
    hits = response.get("hits", {})
    return {
        "total": hits.get("total", {}).get("value"),
        "hits": [
            {
                "id": hit["_id"],
                "score": hit.get("_score"),
                "title": hit["_source"].get("title"),
                "category": hit["_source"].get("category"),
                "views": hit["_source"].get("views"),
                "published_at": hit["_source"].get("published_at"),
                **({"highlight": hit["highlight"]} if "highlight" in hit else {}),
            }
            for hit in hits.get("hits", [])
        ],
        **({"aggregations": response["aggregations"]} if "aggregations" in response else {}),
    }


def pretty(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, indent=2)
