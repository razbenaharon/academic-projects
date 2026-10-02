# Adversarial and Contrastive Learning

SVHN classification, FGSM perturbations and adversarial training, followed by SimCLR representation learning and an NT-Xent loss implementation.

## Contribution and provenance

`HW3.ipynb` preserves the practical implementations and discussions within the supplied course notebook.

## Running

Use a compatible Python/PyTorch notebook environment with torchvision, numpy, matplotlib and scikit-learn. Review dataset extraction paths before running; several cells train models and may download data.

## Evidence and limits

No full training or robustness benchmark was rerun. Check epsilon against the input scaling, train/evaluation modes, split usage and positive/negative masks before relying on reported comparisons.

Imported coursework outputs and personal submission metadata have been removed from the public copy. The original OneDrive materials were not edited.
