# Adversarial and Contrastive Learning

SVHN classification, FGSM perturbations and adversarial training, followed by SimCLR representation learning and an NT-Xent loss implementation.

## Contribution and provenance

`HW3.ipynb` preserves the practical implementations and discussions within the supplied course notebook.

## Running

Use a compatible Python/PyTorch notebook environment with torchvision, numpy, matplotlib and scikit-learn. Review dataset extraction paths before running; several cells train models and may download data.

## Evidence and limits

No full training or robustness benchmark was rerun. Check epsilon against the input scaling, train/evaluation modes, split usage and positive/negative masks before relying on reported comparisons.

Imported coursework outputs and personal submission metadata have been removed from the public copy. The original OneDrive materials were not edited.

## FGSM input domain and historical results

The SVHN model receives per-channel normalized tensors. `attacks.py` now clamps perturbed
inputs to `-mean/std` through `(1-mean)/std`, the interval corresponding to raw pixels in
[0, 1]. Clamping the normalized tensor itself to [0, 1] would be incorrect.

Epsilon retains its original **normalized-input units**. In raw pixel units the per-channel
budget is epsilon times that channel's standard deviation, not epsilon. The notebook imports
the repaired function; `clamp=False` explicitly restores the original unconstrained formula
for historical comparisons. Clipped training/evaluation results have not been rerun, so
historical robustness figures must not be attributed to this repaired attack.
