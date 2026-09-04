# Wikipedia Hybrid Retrieval

**Course:** Technion — Section B · **Individual project**

Answer natural-language questions over a Wikipedia corpus by returning ranked `page_id`s, scored on **NDCG@10**. The interesting constraint is that query time is measured: the index is built offline, and the timed stage only embeds the query and ranks.

The ranker is a **hybrid** — dense semantic similarity plus three lexical signals, combined with tuned weights:

| Signal | Weight | Why it earns its place |
|---|---|---|
| MiniLM semantic similarity | 0.60 | Handles paraphrase, where the question shares no vocabulary with the article |
| BM25 over the article **lead** | 0.30 | A Wikipedia lead states what the page *is*; scoring it separately beats scoring the whole body, which dilutes the signal across a long article |
| Query-term coverage | 0.10 | A cheap guard against a semantically plausible page that omits a key entity outright |

Full-article BM25, title overlap, popularity, pseudo-relevance feedback and proximity scoring are all implemented and **switched off** — they scored worse on the public queries than the three above. They are left in `retrieve.py` rather than deleted, because the fact that they did not help is part of the result.

> **Reproducibility.** Two things this repository cannot ship: the `data/Wikipedia Entries/` corpus, which is course-provided and not redistributable, and `artifacts/`, roughly 250 MB of prebuilt index tensors that `scripts/build_index.py` regenerates from the corpus. The 29 public queries with their relevance judgements *are* included, in `data/public_queries.json`. With the corpus in place, `python scripts/build_index.py && python scripts/eval_public.py` reproduces the evaluation end to end.
>
> No NDCG@10 figure is quoted here because none was recorded at submission time, and inventing one is not an option. `scripts/eval_public.py` prints it for anyone with the corpus.

---

Video presentation: [Google Drive](https://drive.google.com/file/d/1OTeE8505G-K7uFsKdHm5gg1vetxAvULA/view?usp=sharing)

The program takes a list of search queries and returns Wikipedia `page_id`
results for each. The grader only checks the top 10, so the goal was NDCG@10
with a query time that stayed reasonable.

## How the Project Works

The main entry point is:

```python
from main import run

results = run(queries)
```

`queries` is a list of strings, and the output is a list of lists. Each inner
list contains page ids ordered from most relevant to least relevant.

The index is built offline and saved in the `artifacts/` folder. During the
actual run, the code loads these files and only does the query embedding and
ranking part.

## Setup

From the project folder, install the requirements:

```bash
pip install -r requirements.txt
```

The main packages I used are:

- `sentence-transformers` for MiniLM embeddings
- `numpy` for the scoring calculations
- `nltk` for stemming words
- `faiss-cpu`, which is included in the requirements although the current main
  retriever does not depend on it

The Wikipedia files should be in:

```text
data/Wikipedia Entries/
```

Each entry is expected to have `page_id`, `title`, and `content`.

## Running

To test the public queries:

```bash
python scripts/eval_public.py
```

To rebuild the artifacts first:

```bash
python scripts/build_index.py
python scripts/eval_public.py
```

Building the index is not part of the timed query stage. It just creates the
files that are later loaded by `run()`.

## Retrieval Method

I used a hybrid retrieval approach:

- semantic similarity with `sentence-transformers/all-MiniLM-L6-v2`
- BM25-style lexical scoring
- a separate BM25 score for the beginning of the article, since the first part
  of a Wikipedia page usually contains the most important information
- a small coverage score that checks how many query terms appear in a page

The final score is a weighted combination of these parts. The current weights in
`retrieve.py` are:

```text
semantic:   0.60
BM25 lead:  0.30
coverage:   0.10
```

I also kept some extra scoring code in the project, like full-article BM25,
title overlap, popularity, pseudo-relevance feedback, and proximity scoring.
Those are currently turned off because this combination gave better results on
the public queries.

## Main Files

```text
main.py                 run() entry point for the grader
retrieve.py             query-time ranking code
index.py                builds and loads index artifacts
embed.py                document and query embeddings
utils.py                tokenization, paths, and corpus helpers
eval.py                 NDCG@10 evaluation code
tune_hyperparameters.py offline tuning script
scripts/build_index.py  rebuilds artifacts
scripts/eval_public.py  evaluates public queries
artifacts/              saved index files (not committed - rebuild with scripts/build_index.py)
data/                   queries and Wikipedia entries
```

## Notes

- CUDA is used automatically if PyTorch detects a GPU.
- If there is no GPU, the code still works on CPU, but embedding can be slower.
- The public tuning was done with `tune_hyperparameters.py`, then I copied the
  best constants into `retrieve.py`.
