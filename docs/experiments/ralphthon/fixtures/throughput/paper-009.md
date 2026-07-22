# Mock Paper 009: Multilingual Prompt Compression

Synthetic fixture; not a real paper or experimental result.

## Abstract (page 1)

The paper compresses task instructions by deleting tokens ranked as redundant. It claims shorter prompts with preserved multilingual task accuracy.

## Method (page 2)

Token importance is estimated in English and the same deletion mask is transferred to four languages. A random-deletion baseline uses the same compression ratio.

## Results (page 3)

Table 3 reports average exact match of 63.2 before compression, 62.8 after importance-based deletion, and 58.1 after random deletion. Per-language scores show a 5.4-point drop for the lowest-resource language.

## Limitations (page 4)

The average masks heterogeneous language effects. Native-speaker assessment and non-Latin tokenization analysis are absent.
