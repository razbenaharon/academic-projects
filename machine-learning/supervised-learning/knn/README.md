# KNN from Scratch

A NumPy classifier using Minkowski distance and majority voting. `ML1.py` explores synthetic Gaussian classes, k and training sample size; it adds experimental context to the implementation.

## Contribution and provenance

`HW1.py` contains my classifier within the course interface. `ML1.py` is the experiment driver.

## Running

Python with numpy, pandas and matplotlib. Run `python HW1.py INPUT.csv K P` using a headerless table with the label in the last column. Run `python ML1.py` for synthetic experiments.

## Evidence and limits

Public-copy repairs add absolute differences, fix invalid neighbor-boundary indexing and make ties deterministic: neighbors by distance then label; majority ties by nearest supporting neighbor then label. These repairs may change historical predictions; the original results were not rerun.

Imported coursework outputs and personal submission metadata have been removed from the public copy. The original OneDrive materials were not edited.
