# Mock Paper 001: Calibrated Small-Data Classification

Synthetic fixture; not a real paper or experimental result.

## Abstract (page 1)

We compare a temperature-scaled linear classifier with an uncalibrated linear baseline on a frozen synthetic binary dataset. The proposed method lowers expected calibration error while keeping accuracy nearly unchanged.

## Method (page 2)

The train, validation, and test splits are fixed before tuning. Temperature is selected on the validation split. The same features, optimizer, and test set are used for both methods.

## Results (page 3)

Table 1 reports mean test accuracy over five seeds: baseline 0.812 and proposed 0.814. Expected calibration error is 0.118 for the baseline and 0.061 for the proposed method. Standard deviations are reported only for accuracy.

## Limitations (page 4)

The study uses one synthetic dataset and does not report uncertainty for calibration error. No comparison with isotonic calibration is included.
