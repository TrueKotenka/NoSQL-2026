#!/usr/bin/env python3
"""Run the assignment scenarios and save real request/response transcripts."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from es_client import pretty, request


ROOT = Path(__file__).resolve().parent.parent
SCREENSHOTS = ROOT / "screenshots"
SCREENSHOTS.mkdir(exist_ok=True)


def save(name: str, content: str) -> None:
    path = SCREENSHOTS / f"{name}.log"
    path.write_text(content.rstrip() + "\n", encoding="utf-8")
    print(path.relative_to(ROOT))


def command(*args: str) -> str:
    completed = subprocess.run(args, cwd=ROOT, capture_output=True, text=True, check=True)
    return completed.stdout + completed.stderr


def python(script: str, *args: str) -> str:
    return command(sys.executable, str(ROOT / "scripts" / script), *args)


def main() -> None:
    save("01_container", "$ docker compose ps\n" + command("docker", "compose", "ps"))
    save("02_connection", "GET /\n" + pretty(request("GET", "/")))
    save(
        "03_mapping_count",
        "GET /videos/_mapping\n" + pretty(request("GET", "/videos/_mapping"))
        + "\nGET /videos/_count\n" + pretty(request("GET", "/videos/_count")),
    )

    query_names = [
        ("04_match", "match"),
        ("05_match_phrase", "match_phrase"),
        ("06_multi_match", "multi_match"),
        ("07_term", "term"),
        ("08_range", "range"),
        ("09_exists", "exists"),
        ("10_bool_must_filter", "bool_must_filter"),
        ("11_bool_should", "bool_should"),
        ("12_bool_must_not", "bool_must_not"),
        ("15_score_sort", "sort_score"),
        ("18_fuzziness", "fuzziness"),
        ("19_highlight", "highlight"),
        ("20_agg_terms", "agg_terms"),
        ("21_agg_avg_filtered", "agg_avg_filtered"),
        ("22_agg_date_histogram", "agg_date_histogram"),
    ]
    for filename, query_name in query_names:
        save(filename, python("query.py", query_name))

    save("13_filter_comparison", python("query.py", "compare_unfiltered") + "\n" + python("query.py", "compare_filtered"))
    save("14_sort_asc_desc", python("query.py", "sort_views_asc") + "\n" + python("query.py", "sort_views_desc"))
    save("16_pagination", python("check_pagination.py"))
    save("17_score_comparison", python("compare_scores.py"))
    save("23_update", python("mutations.py", "update"))
    save("24_delete", python("mutations.py", "delete"))


if __name__ == "__main__":
    main()
