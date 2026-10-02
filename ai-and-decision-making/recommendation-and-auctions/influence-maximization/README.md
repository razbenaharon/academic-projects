# Influence Maximization

Budgeted selection in a network using simulated influence, graph features, candidate pools, greedy selection and experiment sweeps.

## Contribution and provenance

`influence_maximization.py` contains the submission/pipeline; `campaign_experiments.py` and `optimize_shield.py` explore variants; `eda.ipynb` provides exploration.

## Running

Python with numpy, pandas and networkx. Supply the graph, costs and probabilities expected by the source. Experiment wrappers now import `influence_maximization`.

## Evidence and limits

Referenced symbols exist and a tiny synthetic simulation is checked. Original graph data are absent, so full sweeps and reported influence were not rerun. Submission output names use placeholders.

Imported coursework outputs and personal submission metadata have been removed from the public copy. The original OneDrive materials were not edited.
