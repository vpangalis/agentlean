"""ADR-0089 (W20, DEF-288): the countries and sites a case can be located at — read from `config/sites.json`, which
each customer ships as configuration (C5): no directory lookup, no network call."""
from __future__ import annotations

import functools
import json
from pathlib import Path
from typing import Any

SITES_FILE = Path(__file__).resolve().parents[2] / "config" / "sites.json"
#: What a case or person with no location shows (W20: existing cases read "not set").
NOT_SET = "not set"


@functools.lru_cache(maxsize=1)
def countries() -> tuple[dict[str, Any], ...]:
    """The configured countries, each {code, name, sites}, in the file's order."""
    data = json.loads(SITES_FILE.read_text(encoding="utf-8"))
    return tuple({"code": str(c["code"]).upper(), "name": str(c["name"]), "sites": [str(s) for s in c["sites"]]}
                 for c in data["countries"])


def check(country: str, site: str) -> str:
    """Why `country` and `site` are not a location from the lists, in plain words — "" when they are."""
    found = next((c for c in countries() if c["code"] == str(country or "").strip().upper()), None)
    if found is None:
        return "Choose the country from the list."
    if str(site or "").strip() not in found["sites"]:
        return f"Choose the site from the list for {found['name']}."
    return ""


def label(location: Any) -> str:
    """A location as the page and the report say it — "Linz, Austria" — or "not set"."""
    loc = location if isinstance(location, dict) else getattr(location, "model_dump", lambda: {})()
    code, site = str(loc.get("country") or "").upper(), str(loc.get("site") or "")
    name = next((c["name"] for c in countries() if c["code"] == code), code)
    return f"{site}, {name}" if site and name else name or NOT_SET


__all__ = ["SITES_FILE", "NOT_SET", "countries", "check", "label"]
