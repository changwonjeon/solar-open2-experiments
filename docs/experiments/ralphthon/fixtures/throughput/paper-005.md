# Mock Paper 005: Interactive Label Cleaning

Synthetic fixture; not a real paper or experimental result.

## Abstract (page 1)

The paper presents an interface that ranks potentially incorrect labels for human review. It claims that prioritization reduces inspection effort.

## Method (page 2)

A disagreement score combines model uncertainty and neighbor inconsistency. The evaluation uses a frozen synthetic annotation set with injected label flips. Reviewers inspect ranked items in order.

## Results (page 3)

Figure 3 reports that the method finds 72 of 100 injected errors within 200 inspections; random ordering finds 21. The interface time and reviewer disagreement are not measured.

## Limitations (page 4)

Injected independent flips may not represent systematic real annotation errors. No human-subject deployment was conducted.
