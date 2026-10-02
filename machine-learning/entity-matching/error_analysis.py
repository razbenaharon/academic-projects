"""
Task 2 — Automated error analysis (false-negative extraction).

Runs the honest 20-seed x 5-fold CV and tracks, per known match, how often it
was pushed OUT of the top-2000 when it was a held-out positive (miss_rate), and
how far past the cutoff it landed (median rank in the model's full ranked pool).
Then it joins the raw metadata (title / manufacturer / price) from tableA and
tableB and prints the hardest pairs side-by-side for manual audit, plus the key
similarity features that explain why each is hard.

Because the two-sided k-NN pool has a 1.000 recall ceiling on the 100 known
matches, every miss here is a RANKING failure, not a retrieval failure — the
match is in the pool but scored below the 2000-th candidate. The output tells us
what signal a new feature would need to add (Task 3).
"""
import numpy as np
import pandas as pd

import em_core as C

BM_K1, BM_B = 1.5, 0.75     # same BM25 params as solution.py
MISS_THRESHOLD = 0.5        # "false negative" = missed in >= 50% of held-out trials
SEEDS = range(20)


def main():
    A, B, known = C.load_tables()
    ctx = C.build_pool(A, B, known)
    pool = [tuple(p) for p in ctx["pool"]]
    pool_ix = {p: i for i, p in enumerate(pool)}
    ceiling = len(set(pool) & known) / len(known)
    print(f"pool={len(pool)}  ceiling recall on known={ceiling:.3f}  "
          f"(every miss below is a ranking failure, not retrieval)")

    Xb, cb = C.base_features(ctx)
    Xm, cm = C.bm25_features(ctx, BM_K1, BM_B)
    X = np.hstack([Xb, Xm])
    cols = cb + cm
    col = {c: i for i, c in enumerate(cols)}

    stats = C.cv_perpair(X, ctx, seeds=SEEDS)

    Ai = {int(v): i for i, v in enumerate(A["id"])}
    Bi = {int(v): i for i, v in enumerate(B["id"])}

    recs = []
    for (ida, idb), st in stats.items():
        miss_rate = st["misses"] / st["trials"] if st["trials"] else np.nan
        med_rank = int(np.median(st["ranks"])) if st["ranks"] else -1
        ia, ib = Ai[ida], Bi[idb]
        xrow = X[pool_ix[(ida, idb)]]
        recs.append({
            "id_a": ida, "id_b": idb,
            "miss_rate": round(miss_rate, 3),
            "median_rank": med_rank,
            "char_sim": round(xrow[col["sc"]], 3),
            "word_sim": round(xrow[col["sw"]], 3),
            "jaccard": round(xrow[col["jac"]], 3),
            "bm25_max": round(xrow[col["bm25_max"]], 3),
            "price_known": int(xrow[col["pknown"]]),
            "price_reldiff": round(xrow[col["pdiff"]], 3),
            "manuf_in_B": int(xrow[col["man_in"]]),
            "A_title": A["title"].iloc[ia],
            "A_manuf": A["manufacturer"].iloc[ia],
            "A_price": A["price"].iloc[ia],
            "B_title": B["title"].iloc[ib],
            "B_manuf": B["manufacturer"].iloc[ib],
            "B_price": B["price"].iloc[ib],
        })

    df = pd.DataFrame(recs).sort_values(
        ["miss_rate", "median_rank"], ascending=[False, False]).reset_index(drop=True)
    df.to_csv(C.BASE + "false_negatives.csv", index=False)

    fn = df[df["miss_rate"] >= MISS_THRESHOLD]
    print(f"\n{len(fn)} of {len(df)} known matches are FALSE NEGATIVES "
          f"(missed in >= {int(MISS_THRESHOLD*100)}% of held-out trials).")
    print(f"Full ranked table saved to false_negatives.csv\n")
    print("=" * 100)
    for _, r in fn.iterrows():
        print(f"[miss_rate={r.miss_rate}  median_rank={r.median_rank}  "
              f"char_sim={r.char_sim}  jaccard={r.jaccard}  bm25={r.bm25_max}  "
              f"price_known={r.price_known}  manuf_in_B={r.manuf_in_B}]")
        print(f"  A({r.id_a}): {r.A_title}")
        print(f"          manuf={r.A_manuf!r}  price={r.A_price}")
        print(f"  B({r.id_b}): {r.B_title}")
        print(f"          manuf={r.B_manuf!r}  price={r.B_price}")
        print("-" * 100)

    # summary: are hard pairs near-misses (fixable by ranking) or far-misses?
    if len(fn):
        near = (fn["median_rank"] < 4000).sum()
        print(f"\nOf the {len(fn)} false negatives: {near} are near-misses "
              f"(median rank < 4000 -> a better ranker could recover them), "
              f"{len(fn)-near} are far-misses (weak text overlap -> need a new signal).")


if __name__ == "__main__":
    main()
