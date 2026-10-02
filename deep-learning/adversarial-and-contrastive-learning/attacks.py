"""FGSM for SVHN tensors normalized per channel.

epsilon is measured in normalized-input units, as in the original coursework.
Set clamp=False only to reproduce the original unconstrained perturbation.
"""
import math

import torch

SVHN_MEAN = (0.4377, 0.4438, 0.4728)
SVHN_STD = (0.1980, 0.2010, 0.1970)


def fgsm_attack(image, epsilon, data_grad, mean=SVHN_MEAN, std=SVHN_STD, *, clamp=True):
    if not math.isfinite(epsilon) or epsilon < 0:
        raise ValueError("epsilon must be finite and nonnegative")
    if image.ndim < 3 or image.shape != data_grad.shape:
        raise ValueError("Expected matching CHW or NCHW image/gradient tensors")
    perturbed = image + epsilon * data_grad.sign()
    if not clamp:
        return perturbed
    if len(mean) != image.shape[-3] or len(std) != len(mean) or any(s <= 0 for s in std):
        raise ValueError("mean/std must match channels with positive standard deviations")
    shape = (1,) * (image.ndim - 3) + (len(mean), 1, 1)
    means = image.new_tensor(mean).reshape(shape)
    stds = image.new_tensor(std).reshape(shape)
    # Bounds corresponding to raw pixels in [0, 1]; [0, 1] is NOT the
    # correct interval for the normalized model input.
    return torch.maximum(torch.minimum(perturbed, (1 - means) / stds), -means / stds)
