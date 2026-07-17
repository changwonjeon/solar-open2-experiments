---
type: Frozen Evaluation Contract
title: Seeded Review Quality Contract
description: Agent execution 전에 동결한 synthetic gold, baseline, matching, and pass thresholds.
tags: [ralphthon, track-2, quality, fixture]
timestamp: 2026-07-12T12:40:00+09:00
status: frozen
---

# Scope

The ten papers are synthetic test inputs. Their statements and numbers are not real research results. Quality evaluation covers whether a review identifies seeded strengths and weaknesses at the right paper location; it does not estimate live-platform review quality.

# Frozen unit of evaluation

Each gold or predicted finding has `paper_id`, `finding_type`, `locator`, and `text`. `finding_type` is exactly `strength` or `weakness`. The gold file is `gold.json`. The naive baseline output is `naive-single-pass.json`.

# Location-match rule

A prediction matches a gold finding only when all three keys match after normalization:

1. `paper_id` is byte-for-byte equal.
2. `finding_type` is byte-for-byte equal.
3. `locator` is lowercased, surrounding whitespace is stripped, internal whitespace is collapsed, and then it is byte-for-byte equal.

No semantic, adjacent-page, section-only, or partial-credit match is allowed. Matching is one-to-one: a gold item can be consumed once, and every extra prediction is a false positive. Finding prose is retained for audit but is not used to rescue a location mismatch.

# Metrics

- `TP`: predicted findings matched one-to-one to gold.
- `FP`: predicted findings not matched to unused gold.
- `FN`: gold findings left unmatched.
- `precision = TP / (TP + FP)`; zero predictions give precision 0.
- `recall = TP / (TP + FN)`.
- `F1`: harmonic mean of precision and recall; zero denominator gives 0.
- `paper_coverage`: papers with at least one TP divided by 10.
- `location_accuracy = TP / prediction_count`.

# Frozen baseline

The naive single-pass baseline takes only the first explicit result sentence selected from each paper and emits one finding. It does not revisit methods, limitations, or unsupported claims. The frozen baseline has `TP=10`, `FP=0`, `FN=10`, precision `1.0`, recall `0.5`, F1 `0.666667`, paper coverage `1.0`, and location accuracy `1.0`.

# Candidate threshold

A candidate quality run passes only when all conditions hold:

- precision at least `0.80`;
- recall at least `0.80`;
- F1 at least `0.80`;
- paper coverage exactly `1.0`;
- location accuracy at least `0.80`;
- F1 exceeds the frozen naive baseline by at least `0.10`.

Schema validity and runtime throughput are separate gates. A test fixture or mock response must never be described as a live review result.
