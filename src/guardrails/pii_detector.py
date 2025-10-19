"""Simple PII detection helpers."""

from __future__ import annotations

import json
import re
from typing import Iterable, List, Set, Union

PII_PATTERNS = {
    "phone_long": re.compile(r"\b(?:\+?\d{1,3}[-.\s]?)?(?:\(?\d{3}\)?[-.\s]?){2}\d{4}\b"),
    "phone_short": re.compile(r"\b\d{3}[-.\s]?\d{4}\b"),
    "email": re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}"),
}


def _to_iterable_text(data: Union[str, dict, Iterable]) -> Iterable[str]:
    """Yield string fragments from arbitrary data structures."""
    if isinstance(data, str):
        yield data
    elif isinstance(data, dict):
        yield json.dumps(data, ensure_ascii=False)
    elif isinstance(data, Iterable):
        for item in data:
            yield from _to_iterable_text(item)
    else:
        yield str(data)


def detect_pii(data: Union[str, dict, Iterable]) -> List[str]:
    """Return all detected PII snippets within the provided data."""
    matches: Set[str] = set()
    for text in _to_iterable_text(data):
        for pattern in PII_PATTERNS.values():
            matches.update(pattern.findall(text))
    return sorted(matches)


def has_pii(data: Union[str, dict, Iterable]) -> bool:
    """Return True when any PII is present in the data."""
    return bool(detect_pii(data))
