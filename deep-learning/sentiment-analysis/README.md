# Generalization and IMDB Sentiment

The assignment combines a random-label MNIST memorization experiment with preprocessing, RNN and bidirectional LSTM sentiment classification.

## Contribution and provenance

`HW2.ipynb` contains my practical implementations and written discussion within the supplied assignment notebook.

## Running

Python with torch, torchvision, numpy, pandas, matplotlib and scikit-learn. Supply the IMDB archive expected by the loading cells and update local paths. Run the notebook in order; training can be lengthy.

## Evidence and limits

The random-label experiment is included here to preserve the original assignment context. Outputs/embedded submission images are omitted. Historical discussions are not newly rerun results; audit train/test use before treating model comparisons as final benchmarks.

Imported coursework outputs and personal submission metadata have been removed from the public copy. The original OneDrive materials were not edited.

## Historical test-set model selection

The RNN training cell keeps the epoch with the highest test accuracy and reloads those
weights. Thus that test set participates in checkpoint selection: its reported score is
not an untouched final holdout. The notebook calls this early stopping, but the loop still
runs the configured epochs; it is best-checkpoint selection rather than stopping training
early. This migration documents the original protocol without silently changing its
splits or historical results. A fresh evaluation should select on a validation subset of
training data and reserve test data for the final evaluation.
