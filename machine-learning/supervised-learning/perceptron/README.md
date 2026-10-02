# Multiclass Perceptron

Linear class scores and online mistake-driven updates implemented directly with NumPy.

## Contribution and provenance

`HW2_wet.py` implements the classifier within the course interface.

## Running

Python with numpy and pandas. Run `python HW2_wet.py INPUT.csv`; the headerless CSV ends with a label column.

## Evidence and limits

The original loop could run forever on inseparable data. The public copy uses `max_epochs=1000` and exposes `converged_` and `n_epochs_`. It keeps the last weights when the cap is reached. `fit` returns whether training converged within the cap; False is not a proof of inseparability. Repeated calls reset convergence state. There is no added bias term or changed training objective.

Imported coursework outputs and personal submission metadata have been removed from the public copy. The original OneDrive materials were not edited.
