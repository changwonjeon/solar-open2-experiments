"""Locate the repository source package from staged or installed skill paths."""

from __future__ import annotations

import sys
from pathlib import Path


def bootstrap_source() -> Path:
    current = Path(__file__).resolve()
    for parent in current.parents:
        source = parent / "src"
        if (source / "ralphthon_track2_review_agent").is_dir():
            source_text = str(source)
            if source_text not in sys.path:
                sys.path.insert(0, source_text)
            return source
    raise RuntimeError("repository src/ralphthon_track2_review_agent was not found")
