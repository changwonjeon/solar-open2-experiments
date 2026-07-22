# Mock Paper 002: Sparse Retrieval with Cached Embeddings

Synthetic fixture; not a real paper or experimental result.

## Abstract (page 1)

We propose a cache-aware sparse retriever intended to reduce query latency without changing the ranking model. The paper claims a twofold speedup at equal retrieval quality.

## Method (page 2)

Queries are evaluated against a frozen collection. The baseline recomputes document embeddings, whereas the proposed system reuses cached embeddings. Both systems run on the same CPU host.

## Results (page 3)

Table 2 reports median latency of 84 ms for the baseline and 39 ms for the cached system. Recall@10 is 0.734 and 0.731, respectively. The paper does not report tail latency or cache-warmup cost.

## Limitations (page 4)

Only one collection size and one hardware configuration are tested. Cache invalidation under document updates is not evaluated.
