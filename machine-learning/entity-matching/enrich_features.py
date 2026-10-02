"""
Task 3 (validation) — downstream pairwise features from the enrichment, tested
honestly through the same multi-seed CV.

Turns the three enrichment columns (from local_enrich.py / enrich_*.json) into
high-signal binary pair features and measures whether adding each group to the
base+BM25 ranker actually improves 20-seed CV recall@2000. Groups:

    ebrand : brand_match, brand_conflict
    ever   : version_match (overlap count), version_mismatch_conflict
    ecat   : category_match, category_conflict

Decision rule (same as Task 1): a group is ADOPTED only if it beats the
base+BM25 baseline by more than one standard error of the CV mean. With 100
labels, hand-crafted brand/version features have historically overfit and hurt
CV — the honest expectation is that the *conflict* features are the only ones
with a chance, and groups that don't clear the bar are reported and dropped.
"""
import json
import numpy as np
import pandas as pd

import em_core as C

BM_K1, BM_B = 1.5, 0.75
SEEDS = range(20)


def load_enrichment():
    with open(C.BASE + "enrich_A.json") as f:
        eA = {int(k): v for k, v in json.load(f).items()}
    with open(C.BASE + "enrich_B.json") as f:
        eB = {int(k): v for k, v in json.load(f).items()}
    return eA, eB


def enrichment_features(ctx, eA, eB):
    """Return {group_name: (matrix, colnames)} for the pool."""
    pool = ctx["pool"]
    brand, ver, cat = [], [], []
    for (ida, idb) in pool:
        a, b = eA[ida], eB[idb]
        ba, bb = a["standardized_brand"], b["standardized_brand"]
        bmatch = 1.0 if (ba and bb and ba == bb) else 0.0
        bconf = 1.0 if (ba and bb and ba != bb) else 0.0
        brand.append([bmatch, bconf])

        va, vb = set(a["clean_version"]), set(b["clean_version"])
        vmatch = float(len(va & vb))
        vconf = 1.0 if (va and vb and not (va & vb)) else 0.0
        ver.append([vmatch, vconf])

        ca, cb = a["product_category"], b["product_category"]
        cmatch = 1.0 if ca == cb else 0.0
        cconf = 1.0 if ca != cb else 0.0
        cat.append([cmatch, cconf])

    return {
        "ebrand": (np.array(brand), ["brand_match", "brand_conflict"]),
        "ever": (np.array(ver), ["version_match", "version_mismatch_conflict"]),
        "ecat": (np.array(cat), ["category_match", "category_conflict"]),
    }


def main():
    A, B, known = C.load_tables()
    ctx = C.build_pool(A, B, known)
    Xb, cb = C.base_features(ctx)
    Xm, cm = C.bm25_features(ctx, BM_K1, BM_B)
    Xbase = np.hstack([Xb, Xm])
    groups = enrichment_features(ctx, *load_enrichment())

    def ev(X):
        f = C.cv_recall(X, ctx, seeds=SEEDS)
        return f.mean(), f.std(), f.std() / np.sqrt(len(f))

    print("=== enrichment feature validation (20-seed CV recall@2000) ===\n", flush=True)
    bm, bs, bse = ev(Xbase)
    print(f"base+bm25 (baseline)          {bm:.4f} +/-{bs:.4f}   SE={bse:.4f}", flush=True)
    thresh = bm + bse
    print(f"adoption threshold (base+1SE) = {thresh:.4f}\n", flush=True)

    results = {}
    for g, (Xg, names) in groups.items():
        m, s, se = ev(np.hstack([Xbase, Xg]))
        results[g] = m
        flag = "ADOPT" if m > thresh else "drop"
        print(f"base+bm25+{g:<7} {m:.4f} +/-{s:.4f}   delta={m-bm:+.4f}   [{flag}]  ({', '.join(names)})",
              flush=True)

    # all enrichment groups together
    Xall = np.hstack([Xbase] + [g[0] for g in groups.values()])
    m, s, se = ev(Xall)
    flag = "ADOPT" if m > thresh else "drop"
    print(f"base+bm25+ALL-enrich   {m:.4f} +/-{s:.4f}   delta={m-bm:+.4f}   [{flag}]", flush=True)

    adopted = [g for g, mv in results.items() if mv > thresh]
    print(f"\nADOPTED groups (> baseline + 1 SE): {adopted if adopted else 'none'}")
    if not adopted:
        print("Conclusion: enrichment features do not robustly beat base+bm25 on the "
              "100-label CV -> keep the 18-feature solution.py ranker. The columns and "
              "conflict signals remain available in enrich_*.json for future use / a "
              "larger labelled set.")


if __name__ == "__main__":
    main()
