# Mock Paper 003: Counterfactual Forecast Diagnostics

Synthetic fixture; not a real paper or experimental result.

## Abstract (page 1)

This work adds counterfactual perturbations to a forecasting diagnostic suite. It argues that the diagnostics reveal shortcut reliance missed by aggregate error metrics.

## Method (page 2)

The diagnostic replaces one covariate at a time with a matched draw. Forecast models are not retrained. A perturbation is flagged when prediction change exceeds a threshold selected on the same evaluation set.

## Results (page 3)

Figure 2 shows that 18 of 40 models are flagged. The authors manually inspect four flagged models and describe three as shortcut-dependent. No unflagged models are inspected.

## Limitations (page 4)

Threshold selection and evaluation reuse the same samples. The small, one-sided manual audit cannot estimate false negatives.
