# Booking Quality Classification

A Spark ML feature pipeline and Random Forest classifier for booking quality, with parameter search and pretrained sentiment enrichment.

## Contribution and provenance

The imported notebook implements the analysis and model pipeline using course data and Spark NLP components.

## Running

Run the notebook on a compatible Databricks/Spark environment with Spark NLP and the original datasets. Update the course storage paths for your own workspace; datasets and downloaded model artifacts are excluded.

## Evidence and limits

Model selection uses TrainValidationSplit, not CrossValidator. SentimentDLModel is pretrained: this work does not train a sentiment architecture from scratch. Outputs and user metadata were removed; the full pipeline was not rerun.

Imported coursework outputs and personal submission metadata have been removed from the public copy. The original OneDrive materials were not edited.
