# Flower VAE

An encoder/decoder VAE, reparameterization and flower-image generation. Generation uses representative class latents rather than a label-conditioned decoder.

## Contribution and provenance

`hw4_code.py` implements the model/training pipeline; `hw4_generation.py` contains reproduction/generation.

## Running

Python with torch, torchvision, numpy, matplotlib and Pillow. Supply the flower images, `category_to_images.json` and locally trusted weights. Training defaults to latent_dim=256. Call `reproduce_hw4(..., latent_dim=...)` with the dimension actually used by your checkpoint.

## Evidence and limits

The public copy aligns generation defaults with training and verifies checkpoint latent dimensions when loading weights. The original weights were not loaded during migration; neither quality nor historical checkpoint compatibility is claimed.

Imported coursework outputs and personal submission metadata have been removed from the public copy. The original OneDrive materials were not edited.
