# Dynamic Exact Vector Index

Packed NumPy storage, capacity growth and deletion by swapping the last active row, with exact similarity search.

## Contribution and provenance

`vector_index.py` contains my implementation of the course interface.

## Running

Install numpy, then import `VectorIndex` from this directory. See its insert/delete/query signatures for batch inputs.

## Evidence and limits

This is exact search, not ANN. No scale or latency benchmark is claimed; memory grows with the stored matrix.

Imported coursework outputs and personal submission metadata have been removed from the public copy. The original OneDrive materials were not edited.
