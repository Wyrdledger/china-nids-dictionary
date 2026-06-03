"""Helpers for reading the China NIDs dictionary.

The functions intentionally use only the Python standard library so downstream
projects can vendor or import this file without package installation.
"""

from __future__ import annotations

import csv
import json
from pathlib import Path
from urllib.request import urlopen


DEFAULT_CURRENT_CSV = (
    "https://raw.githubusercontent.com/"
    "Wyrdledger/china-nids-dictionary/main/data/nids_current.csv"
)


def _open_text(path_or_url: str):
    if path_or_url.startswith(("http://", "https://")):
        return urlopen(path_or_url, timeout=30)
    return Path(path_or_url).open("rb")


def read_nids_csv(path_or_url: str = DEFAULT_CURRENT_CSV) -> list[dict[str, object]]:
    """Read a local or remote NIDs CSV file into a list of dictionaries."""
    with _open_text(path_or_url) as raw:
        text = raw.read().decode("utf-8-sig")

    rows: list[dict[str, object]] = []
    for row in csv.DictReader(text.splitlines()):
        row["report_time_limit_hours"] = int(row["report_time_limit_hours"])
        row["is_current"] = row["is_current"].lower() == "true"
        row["effective_end_date"] = row["effective_end_date"] or None
        rows.append(row)
    return rows


def read_nids_json(path_or_url: str) -> list[dict[str, object]]:
    """Read a local or remote NIDs JSON file into a list of dictionaries."""
    with _open_text(path_or_url) as raw:
        return json.loads(raw.read().decode("utf-8-sig"))


if __name__ == "__main__":
    for item in read_nids_csv():
        print(item["disease_id"], item["disease_name_zh"], item["legal_class"])
