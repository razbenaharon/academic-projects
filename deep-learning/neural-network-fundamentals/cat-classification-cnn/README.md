# Cat Classification CNN

A compact convolutional network with BatchNorm/dropout, augmentation, mixed-precision training and train/validation/test analysis.

## Contribution and provenance

`model.py` extracts the submitted CNN class. `coursework.ipynb` retains the original training workflow without duplicating the class definition.

## Running

Python with torch, torchvision, numpy, matplotlib and Pillow. Supply `big_cats/train`, `big_cats/valid` and `big_cats/test`, then run the notebook from this directory. Windows notebook loaders use zero worker processes.

## Evidence and limits

Weights and images are not included. A synthetic forward-shape test is provided; full training and historical accuracy were not reproduced. Architecture/size comments in the original code are not independently measured benchmarks.

Imported coursework outputs and personal submission metadata have been removed from the public copy. The original OneDrive materials were not edited.
