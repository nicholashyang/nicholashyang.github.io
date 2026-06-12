#!/usr/bin/env python3
"""Fetch publications from INSPIRE and write _data/publications.yml.

This script uses the INSPIRE literature API instead of scraping HTML pages.
It is suitable for local use and for GitHub Actions.
"""

from __future__ import annotations

import json
import os
import pathlib
import re
import sys
import urllib.parse
import urllib.request
from typing import Any


ROOT = pathlib.Path(__file__).resolve().parents[1]
PROFILE_PATH = ROOT / "_data" / "profile.yml"
OUTPUT_PATH = ROOT / "_data" / "publications.yml"
INSPIRE_API = "https://inspirehep.net/api/literature"


def load_author_id() -> str:
    env_value = os.environ.get("INSPIRE_AUTHOR_ID")
    if env_value:
        return env_value.strip()

    profile_text = PROFILE_PATH.read_text()
    match = re.search(r"https://inspirehep\.net/authors/(\d+)", profile_text)
    if not match:
        raise RuntimeError("Could not find an INSPIRE author URL in _data/profile.yml")
    return match.group(1)


def request_publications(author_id: str) -> list[dict[str, Any]]:
    query = urllib.parse.urlencode(
        {
            "q": f"authors.record.$ref:authors/{author_id}",
            "sort": "mostrecent",
            "size": os.environ.get("INSPIRE_SIZE", "100"),
        }
    )
    request = urllib.request.Request(
        f"{INSPIRE_API}?{query}",
        headers={"Accept": "application/json", "User-Agent": "nicholashyang.github.io publication sync"},
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        payload = json.load(response)
    return payload.get("hits", {}).get("hits", [])


def first(values: list[dict[str, Any]] | None, key: str) -> str:
    if not values:
        return ""
    value = values[0].get(key)
    return str(value) if value is not None else ""


def publication_year(metadata: dict[str, Any]) -> str:
    for info in metadata.get("publication_info", []) or []:
        if info.get("year"):
            return str(info["year"])
    if metadata.get("preprint_date"):
        return str(metadata["preprint_date"])[:4]
    if metadata.get("earliest_date"):
        return str(metadata["earliest_date"])[:4]
    return ""


def author_summary(metadata: dict[str, Any], limit: int = 8) -> str:
    names = [
        str(author.get("full_name") or author.get("name") or "").strip()
        for author in metadata.get("authors", []) or []
    ]
    names = [name for name in names if name]
    if not names:
        return "INSPIRE record."
    if len(names) > limit:
        return ", ".join(names[:limit]) + ", et al."
    return ", ".join(names)


def venue(metadata: dict[str, Any]) -> str:
    info = (metadata.get("publication_info") or [{}])[0]
    pieces = []
    for key in ("journal_title", "journal_volume", "artid", "page_start"):
        if info.get(key):
            pieces.append(str(info[key]))
    if pieces:
        return " ".join(pieces)
    if metadata.get("document_type"):
        value = metadata["document_type"]
        if isinstance(value, list):
            return ", ".join(str(item) for item in value)
        return str(value)
    return "INSPIRE"


def links_for(hit: dict[str, Any], metadata: dict[str, Any]) -> list[dict[str, str]]:
    links = []
    control_number = hit.get("id") or metadata.get("control_number")
    if control_number:
        links.append(
            {
                "label": "INSPIRE",
                "url": f"https://inspirehep.net/literature/{control_number}",
            }
        )

    arxiv = first(metadata.get("arxiv_eprints"), "value")
    if arxiv:
        links.append({"label": "arXiv", "url": f"https://arxiv.org/abs/{arxiv}"})

    doi = first(metadata.get("dois"), "value")
    if doi:
        links.append({"label": "DOI", "url": f"https://doi.org/{doi}"})

    return links


def normalize(hit: dict[str, Any]) -> dict[str, Any]:
    metadata = hit.get("metadata", {})
    title = first(metadata.get("titles"), "title") or "Untitled INSPIRE record"
    citations = metadata.get("citation_count")
    meta = venue(metadata)
    if citations is not None:
        meta = f"{meta} · {citations} citations"

    return {
        "title": title,
        "date": publication_year(metadata),
        "meta": meta,
        "summary": author_summary(metadata),
        "links": links_for(hit, metadata),
    }


def yaml_quote(value: str) -> str:
    escaped = value.replace("\\", "\\\\").replace('"', '\\"')
    return f'"{escaped}"'


def write_yaml(items: list[dict[str, Any]]) -> None:
    lines: list[str] = []
    if not items:
        lines.append("[]")
    for item in items:
        lines.append(f"- title: {yaml_quote(item['title'])}")
        lines.append(f"  date: {yaml_quote(item.get('date', ''))}")
        lines.append(f"  meta: {yaml_quote(item.get('meta', ''))}")
        lines.append(f"  summary: {yaml_quote(item.get('summary', ''))}")
        if item.get("links"):
            lines.append("  links:")
            for link in item["links"]:
                lines.append(f"    - label: {yaml_quote(link['label'])}")
                lines.append(f"      url: {yaml_quote(link['url'])}")
        else:
            lines.append("  links: []")
        lines.append("")
    OUTPUT_PATH.write_text("\n".join(lines).rstrip() + "\n")


def main() -> int:
    author_id = load_author_id()
    hits = request_publications(author_id)
    items = [normalize(hit) for hit in hits]
    write_yaml(items)
    print(f"Wrote {len(items)} publication(s) to {OUTPUT_PATH}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"publication sync failed: {exc}", file=sys.stderr)
        raise SystemExit(1)
