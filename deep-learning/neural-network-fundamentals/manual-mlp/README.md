# Manual Backpropagation MLP

A sigmoid hidden layer and softmax classifier with hand-written forward/backward passes, using PyTorch tensor operations without autograd training.

## Contribution and provenance

`model.py` extracts my implementation from the original combined notebook. `coursework.ipynb` retains the MNIST learning-rate experiment and course instructions.

## Running

Python with torch, torchvision and matplotlib. Open the notebook with this directory as its working directory. It downloads MNIST and runs several training jobs. The model can be imported without downloading data.

## Evidence and limits

This is not a NumPy MLP. The public copy fixes an accidental global activation reference. A synthetic gradient check compares manual updates to autograd. The original learning-rate selection uses test accuracy, so its test figures are not an untouched final holdout. That methodology is documented, not silently redesigned.

Imported coursework outputs and personal submission metadata have been removed from the public copy. The original OneDrive materials were not edited.
