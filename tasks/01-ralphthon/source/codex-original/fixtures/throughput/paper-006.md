# Mock Paper 006: Robust Aggregation under Missing Sensors

Synthetic fixture; not a real paper or experimental result.

## Abstract (page 1)

We introduce a masked aggregation rule for multivariate sensor prediction. The method is intended to degrade gracefully as sensors become unavailable.

## Method (page 2)

Training masks sensors independently with probability 0.2. Test conditions remove between zero and four sensors independently. The baseline is trained without masking.

## Results (page 3)

Table 2 reports mean absolute error under four missing sensors: 0.42 for the proposed method and 0.67 for the baseline. With no missing sensors the values are 0.31 and 0.29. Confidence intervals are supplied for every condition.

## Limitations (page 4)

Training and test missingness are both independent, so correlated hardware failures are outside the evaluation.
