# Entity Matching

Candidate blocking for Amazon/Google product records: TF-IDF views, a two-sided pool, BM25 pair signals and a logistic ranker. Strong L2 regularization and low weights for unlabeled pairs address a setting with few known positives.

## Contribution and provenance

My submission is `solution.py`; experiment/support scripts expose variants of the matching approach. `helpers.py` contains the supplied submission contract. Product identifiers are dataset keys, not personal submission identifiers.

## Running

Python with numpy, pandas and scikit-learn. Supply the course `tableA.csv`, `tableB.csv` and trusted `100_matches.pkl` locally, then run `python solution.py` from this directory. The public submission filename uses a placeholder identifier.

## Evidence and limits

The source docstring reports repeated-CV comparisons; they were not rerun in this migration. Avoid presenting them as an independent held-out benchmark. Source scripts read local pickle inputs: use only trusted course artifacts.

Imported coursework outputs and personal submission metadata have been removed from the public copy. The original OneDrive materials were not edited.
