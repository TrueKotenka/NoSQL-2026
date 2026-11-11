#!/usr/bin/env python3
"""Compare ranking and _score with and without title boost."""

from __future__ import annotations

from query import CATALOG, run


def main() -> None:
    rankings = {}
    for name in ("score_description_priority", "score_title_priority"):
        item = next(item for item in CATALOG if item["name"] == name)
        response = run(item)
        rankings[name] = [
            (hit["_id"], hit["_score"]) for hit in response["hits"]["hits"]
        ]
        print()
    print("Сравнение позиций и _score:")
    plain = {identifier: (position, score) for position, (identifier, score) in enumerate(rankings["score_description_priority"], 1)}
    boosted = {identifier: (position, score) for position, (identifier, score) in enumerate(rankings["score_title_priority"], 1)}
    for identifier in sorted(plain):
        before_pos, before_score = plain[identifier]
        after_pos, after_score = boosted[identifier]
        print(f"{identifier}: место {before_pos} → {after_pos}; _score {before_score:.5f} → {after_score:.5f}")


if __name__ == "__main__":
    main()
