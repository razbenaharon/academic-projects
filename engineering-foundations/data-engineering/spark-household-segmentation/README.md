# Household Segmentation on Set-Top-Box Viewing Data

**Course:** Distributed Database Management, Technion — Project 2 · **Team:** Raz Ben Aharon · Lior Malachi

Segment television households from demographics, then characterise each segment by what it actually watches — first as a batch job over Parquet, then as a continuously updated view over a Kafka stream.

---

## Problem

A provider holds two large tables: household demographics, and a log of what every set-top box watched. Separately, neither is worth much. The useful question sits across the join — *which kinds of household watch which kinds of content* — and the answer has to survive being computed on a stream, because both segment membership and viewing habits drift.

## Data

Two Parquet tables from the FWM set-top-box dataset:

| Table | Grain |
|---|---|
| `Project2_demographic.parquet` | one row per household — income, size, age bands, region, other categorical attributes |
| `Project2_static_viewing_data.parquet` | one row per viewing event — household, station, programme, timing |

## Method

```text
demographics ──▶ encode + normalise ──▶ SVD / PCA to 2-D ──▶ K-Means (k = 8)
                                                                   │
                                        ┌──────────────────────────┤
                                        ▼                          ▼
                        distance-stratified subsets      join to viewing log
                                                                   │
                                                                   ▼
                                                    per-cluster station profiles
                                                                   │
Kafka topic ──▶ Structured Streaming ──▶ windowed aggregation ─────┘
```

**Encoding is not a formality here.** K-Means minimises Euclidean distance, so two things had to be true before clustering could mean anything: numerical attributes are normalised, or one wide-range column dominates the objective through its units alone; and categoricals are one-hot encoded rather than integer-indexed, or the model infers an ordering ("region 3 lies between region 2 and region 4") that does not exist.

**SVD before choosing `k`.** Projecting to two dimensions first showed three visible groupings — evidence that the households separate at all, rather than an assumption that they do. Clustering ran afterwards, and the same projection coloured by assignment is the check that the eight clusters are structure and not arbitrary slices of one cloud.

**Stratified subsets.** Each household carries its Euclidean distance from its own centroid — how typical it is of its segment. Households are ranked by that distance *within* cluster, then sampled every 7th and every 11th row. Ranking within cluster keeps each subset proportional to its cluster and spanning typical-to-atypical, which uniform sampling over the whole table would not guarantee; the two coprime strides give subsets that collide only every 77th row.

**Profiles as percentages.** Per-cluster station counts are normalised by the cluster's own total viewing. Raw counts would just rediscover which cluster is biggest.

**Streaming.** The same pipeline over Spark Structured Streaming against a Kafka topic, with an explicit event schema and windowed aggregation. The point is not throughput — it is that a nightly batch cannot show drift while it is happening.

## Contents

```text
spark_household_segmentation.ipynb   the analysis (Databricks/PySpark)
report.pdf                           written answers and discussion
assignment_brief.pdf                 the original course brief
```

## Reproducibility

**This notebook does not run outside Databricks.** It reads from `/dbfs` course mounts, uses Databricks `display()`, and connects to a course Kafka topic. None of those are public, and the dataset is not redistributable. It is preserved as a record of the work, with its outputs intact, rather than as a runnable project — `report.pdf` carries the written analysis.

## Notes on this copy

Migrated from a standalone repository during a portfolio cleanup. Three changes, none touching the analysis:

- Files renamed to drop student ID numbers from their names.
- The markdown cells were rewritten to explain the reasoning; every code cell and all 61 outputs are unchanged.
- Databricks mirrors each `display()` result a second time inside vendor metadata. That duplicate — 1.3 MB — was removed so GitHub renders the notebook.
