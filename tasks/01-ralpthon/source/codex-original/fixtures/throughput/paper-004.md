# Mock Paper 004: Distillation for Tiny Sequence Models

Synthetic fixture; not a real paper or experimental result.

## Abstract (page 1)

We distill a medium sequence model into a smaller recurrent model and claim improved accuracy-efficiency tradeoffs over supervised training.

## Method (page 2)

Teacher logits and labels are combined with a fixed coefficient. The student architecture and training budget match the supervised baseline. Hyperparameters are chosen separately for the two systems.

## Results (page 3)

Table 1 reports token accuracy of 78.4 for supervised training and 80.1 for distillation. Inference latency is 6.2 ms for both because the student architecture is identical. Only one random seed is reported.

## Limitations (page 4)

The teacher training cost is omitted. Single-seed results make the 1.7-point gain uncertain.
