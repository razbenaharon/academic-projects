# MAP Optimization — TREC Robust Retrieval Challenge

**Course:** Information Retrieval Challenge 2025, Technion · **Individual project**

Given a prebuilt Indri index over a subset of the TREC Robust collection, 50 training queries with relevance judgements, and 199 unjudged test queries, maximise **Mean Average Precision**.

**Result: MAP 0.2373** on the training queries, from a hybrid that expands BM25 queries with terms mined by a Dirichlet-smoothed language model under pseudo-relevance feedback — up from 0.2298 for the tuned single-model baseline.

---

## Approach

**1 · Grid search over the classical rankers.** Four sweeps with Indri over Okapi BM25 and Dirichlet smoothing, each with and without pseudo-relevance feedback (PRF), scored by MAP on the 50 judged training queries.

Top configurations:

| Configuration | MAP |
|---|---|
| `dir_mu1000_terms30_w0.6` | **0.2339** |
| `dir_mu1000_terms30_w0.4` | 0.2333 |
| `dir_mu1000_terms20_w0.6` | 0.2328 |
| `dir_mu1000_terms10_w0.4` | 0.2312 |
| `dir_mu1500_terms30_w0.6` | 0.2311 |
| `okapi_no_prf_k1_0.8_b0.5` | 0.2305 |
| `baseline_dir_mu1000` | 0.2298 |

Two things fell out of the sweep:

- Dirichlet with PRF beat every BM25 configuration.
- **PRF did not help BM25** — it usually made it slightly worse. That asymmetry is what suggested combining them rather than picking one.

**2 · The hybrid.** Use each ranker for what it is good at: Dirichlet+PRF to *find* the expansion terms, BM25 to *rank* with them.

For each query, Indri retrieves the top 50 terms from the top 10 documents under the Dirichlet language model. Those terms are filtered (NLTK English stopwords, and anything under 3 characters), the best 20 are kept, and their weights are renormalised to sum to 1. BM25 then runs at its best no-PRF parameters (`k₁ = 0.8`, `b = 0.5`) against a query weighted **60% original / 40% expansion**.

MAP: **0.2373** — the best of the project.

## The mistake worth recording

An early version stripped stopwords from the *queries*. MAP collapsed from ~0.23 to roughly **0.12**.

The index was built **with** stopwords retained. Removing them from the query side created a vocabulary mismatch against the document side, so a routine "clean the input" step nearly halved effectiveness. Preprocessing has to match the index it queries, not general good practice.

## Submitted runs

Three models were submitted, in `run_N.res.txt` (standard TREC format: `qid Q0 docid rank score runid`), 199 test queries × 1000 documents each.

| Run | Model |
|---|---|
| `run_1` | Hybrid — BM25 with Dirichlet-PRF expansion |
| `run_2` | Dirichlet + PRF — μ = 1000, fbDocs = 10, fbTerms = 30, fbOrigWeight = 0.6 |
| `run_3` | BM25 baseline — k₁ = 0.8, b = 0.5, no expansion |

### How different are they, really?

The test queries came with no relevance judgements, so no effectiveness metric can be computed here. What the runs *can* show is whether the three models genuinely rank differently — a fair question to ask of a hybrid before crediting it with anything.

![Mean per-query document overlap between the three submitted runs, at top-10, top-100 and top-1000](assets/run_agreement.png)

Any two runs share roughly three-quarters of each query's results, so about **one document in four differs even in the top 10** — these are three distinct rankings, not one model with cosmetic variations. The pattern at depth is the interesting part: the two single-model runs (Dirichlet+PRF and BM25) agree most with each other (83%), while the hybrid is the *least* similar to the BM25 baseline it is built on (72%). Expansion terms mined by a different ranker pull the ranking somewhere neither parent goes on its own.

Reproduce with:

```bash
pip install matplotlib
python analyze_runs.py
```

## What is and is not here

The grid search and expansion pipeline were driven by Indri command-line invocations against a course-provided index; neither the index nor the driver scripts were part of the submission, so **this project is preserved as its results and its written method**, not as runnable code. [`method_and_results.pdf`](method_and_results.pdf) is the original write-up with the full configuration tables.

`analyze_runs.py` was added afterwards, during a portfolio cleanup, and analyses only the submitted run files.

## Files

```text
method_and_results.pdf   original write-up: index stats, grid search, hybrid, conclusions
run_1.res.txt            hybrid submission          (199 queries x 1000 docs)
run_2.res.txt            Dirichlet + PRF submission
run_3.res.txt            BM25 baseline submission
analyze_runs.py          run-agreement analysis (added later)
assets/run_agreement.png figure produced by the above
```
