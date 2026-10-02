"""
Task 1 — BM25 hyperparameter grid search (k1 x b).

Wraps the existing honest multi-seed CV: for each (k1, b) cell we rebuild ONLY
the 3 BM25 columns, re-attach them to the fixed 15 base features, and measure
downstream CV recall@2000. The BM25 index (term counts, idf, doc lengths) is
built once in em_core.build_pool and is independent of k1/b, so the sweep is
cheap — only the saturation step is recomputed per cell.

Decision rule: adopt a grid winner over the current default (k1=1.5, b=0.75)
ONLY if it beats the default by more than one standard error of the CV mean
(SE ~ std/sqrt(n_folds)); otherwise keep the default. With 100 labels the CV is
noisy, so we do not chase sub-SE differences.
"""
import numpy as np
import pandas as pd

import em_core as C

K1_GRID = [0.2, 0.5, 1.2, 1.6, 2.0]
B_GRID = [0.0, 0.2, 0.5, 0.75, 1.0]
DEFAULT = (1.5, 0.75)

GRID_SEEDS = range(12)   # scan (12 x 5 = 60 folds, SE ~ 0.009)
CONFIRM_SEEDS = range(20)  # confirm winner + default (20 x 5 = 100 folds)


def evaluate(ctx, Xbase, k1, b, seeds):
    Xm, _ = C.bm25_features(ctx, k1, b)
    X = np.hstack([Xbase, Xm])
    folds = C.cv_recall(X, ctx, seeds=seeds)
    return folds.mean(), folds.std(), folds.std() / np.sqrt(len(folds))


def main():
    A, B, known = C.load_tables()
    ctx = C.build_pool(A, B, known)
    print(f"pool={len(ctx['pool'])} ceiling={len(set(ctx['pool']) & known) / len(known):.3f}")
    Xbase, _ = C.base_features(ctx)

    print(f"\n=== BM25 k1 x b grid ({len(K1_GRID)}x{len(B_GRID)}), {len(list(GRID_SEEDS))}-seed CV ===",
          flush=True)
    rows = []
    for k1 in K1_GRID:
        for b in B_GRID:
            m, s, se = evaluate(ctx, Xbase, k1, b, GRID_SEEDS)
            rows.append(dict(k1=k1, b=b, cv_mean=m, cv_std=s, cv_se=se))
            print(f"  k1={k1:<4} b={b:<4}  CV={m:.4f} +/-{s:.4f}", flush=True)

    df = pd.DataFrame(rows).sort_values("cv_mean", ascending=False).reset_index(drop=True)
    df.to_csv(C.BASE + "bm25_grid_results.csv", index=False)
    print("\nTop cells:")
    print(df.head(6).to_string(index=False))

    # confirmation at full seeds
    best = df.iloc[0]
    bk1, bb = float(best["k1"]), float(best["b"])
    print(f"\n=== confirmation at {len(list(CONFIRM_SEEDS))} seeds ===", flush=True)
    dm, ds, dse = evaluate(ctx, Xbase, *DEFAULT, CONFIRM_SEEDS)
    wm, ws, wse = evaluate(ctx, Xbase, bk1, bb, CONFIRM_SEEDS)
    print(f"  default  k1={DEFAULT[0]} b={DEFAULT[1]}: CV={dm:.4f} +/-{ds:.4f} (SE {dse:.4f})")
    print(f"  grid best k1={bk1} b={bb}: CV={wm:.4f} +/-{ws:.4f} (SE {wse:.4f})")

    delta = wm - dm
    print(f"\n  delta (best - default) = {delta:+.4f}   threshold (1 SE) = {dse:.4f}")
    if delta > dse:
        print(f"  -> ADOPT k1={bk1}, b={bb} (robust gain). Update solution.py BM25 params.")
    else:
        print(f"  -> KEEP default k1={DEFAULT[0]}, b={DEFAULT[1]} (no robust improvement; "
              f"difference is within CV noise).")


if __name__ == "__main__":
    main()
