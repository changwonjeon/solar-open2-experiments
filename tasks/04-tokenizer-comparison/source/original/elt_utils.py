#!/usr/bin/env python3
"""
ETRI-style morphological analysis utilities — shared between app.py and verify_models.py.

Provides:
  - LangType enum
  - get_lang_type(text)
  - get_elt_tags(morphs) — filters ETRI-style morphological analysis for Korean text

All functions are stateless and side-effect free.
"""

from __future__ import annotations

from enum import Enum
from typing import Any


class LangType(str, Enum):
    """Language detection result for a text string."""
    KOREAN = "korean"
    ENGLISH = "english"
    MIXED = "mixed"
    OTHER = "other"


def get_lang_type(text: str) -> LangType:
    """
    Detect whether *text* contains Korean (Hangul), English letters,
    both, or neither.

    Returns LangType.KOREAN | LangType.ENGLISH | LangType.MIXED | LangType.OTHER
    """
    has_kr = any("가" <= ch <= "힣" for ch in text)
    has_en = any(ch.isascii() and ch.isalpha() for ch in text)

    if has_kr and has_en:
        return LangType.MIXED
    if has_kr:
        return LangType.KOREAN
    if has_en:
        return LangType.ENGLISH
    return LangType.OTHER


def get_elt_tags(morphs: list[dict[str, Any]]) -> list[tuple[str, str]]:
    """
    Transform ETRI-style morphological-analysis output into a flat list of
    ``(text, ETRI_POS_tag)`` tuples.

    Rules (matching the ETRI tag-set used by the Korean NLP community):

    * Verbs / adjectives (``VV*``, ``VA*``) — keep original tag.
    * Connective endings (``EC``) — if the *next* morpheme is a verb/adjective
      or a content morpheme (``m``), keep ``EC``; otherwise reclassify as
      ``CF`` (connective-final).
    * Sentence-final endings (``EF``) — if the *next* morpheme is another
      sentence-level tag (``EF``, ``EC``, ``CF``), reclassify as ``EC``;
      otherwise keep ``EF``.
    * Everything else — keep original tag unchanged.
    """
    result: list[tuple[str, str]] = []
    n = len(morphs)

    for i, m in enumerate(morphs):
        tag = m.get("type", "")
        text = m.get("text", "")

        if tag.startswith("VV") or tag.startswith("VA"):
            result.append((text, tag))

        elif tag == "EC":
            if i + 1 < n:
                nxt = morphs[i + 1].get("type", "")
                if nxt.startswith("VV") or nxt.startswith("VA") or nxt == "m":
                    result.append((text, "EC"))
                else:
                    result.append((text, "CF"))
            else:
                result.append((text, "CF"))

        elif tag == "EF":
            if i + 1 < n:
                nxt = morphs[i + 1].get("type", "")
                if nxt in {"EF", "EC", "CF"}:
                    result.append((text, "EC"))
                else:
                    result.append((text, "EF"))
            else:
                result.append((text, "EF"))

        else:
            result.append((text, tag))

    return result


# ---------------------------------------------------------------------------
# Lightweight byte-level counter (used by both app.py and verify_models.py)
# ---------------------------------------------------------------------------

def byte_len_of_non_kr(text: str) -> int:
    """Return the byte-length of every non-Hangul character in *text*."""
    return sum(len(ch.encode("utf-8")) for ch in text if not ("가" <= ch <= "힣"))
