#!/usr/bin/env python3
"""Execute the repository's guarded Track 2 batch CLI."""

from __future__ import annotations

from _bootstrap import bootstrap_source

bootstrap_source()

from ralphthon_track2_review_agent.run_batch import main  # noqa: E402


if __name__ == "__main__":
    raise SystemExit(main())
