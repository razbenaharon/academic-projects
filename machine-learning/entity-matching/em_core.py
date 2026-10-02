"""
em_core.py — shared machinery for the blocking experiments.

Factors the proven logic out of solution.py so the experiment scripts
(bm25_grid.py, error_analysis.py, enrich_features.py) are self-contained and
reproduce the exact same feature math and honest evaluation.

Public surface:
    load_tables()                      -> A, B, known
    build_pool(A, B, known)            -> ctx dict (pool, sims, rank maps, ...)
    base_features(ctx)                 -> (n_pool, 15) base feature matrix + names
    bm25_features(ctx, k1, b)          -> (n_pool, 3) BM25 columns + names
    cv_recall(X, ctx, ...)             -> per-fold recall@2000 array (honest CV)
    cv_perpair(X, ctx, ...)            -> per-known-pair miss stats (for error analysis)

The BM25 index (term counts, idf, doc lengths) is built once and is independent
of k1/b — only the saturation step in scoring uses them, which is what makes the
k1xb grid search cheap. The scores match rank_bm25.BM25Okapi to machine precision
(same idf with epsilon floor, same saturation formula), so results are identical
to solution.py's.
"""
import re
import pickle
from collections import defaultdict

import numpy as np
import pandas as pd
import scipy.sparse as sp
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import KFold

BASE = "c:/Users/User/OneDrive - Technion/Python/mini-hackaton/"
KA, KB = 10, 8
BUDGET = 2000


# ----------------------------------------------------------------------------
# load + normalize
# ----------------------------------------------------------------------------
def norm(s):
    if pd.isna(s):
        return ""
    s = str(s).lower()
    s = re.sub(r"[^a-z0-9 ]", " ", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s


def load_tables():
    A = pd.read_csv(BASE + "tableA.csv")
    B = pd.read_csv(BASE + "tableB.csv")
    with open(BASE + "100_matches.pkl", "rb") as f:
        known = {(int(a), int(b)) for a, b in pickle.load(f)}
    for df in (A, B):
        df["t"] = df["title"].map(norm)
        df["m"] = df["manufacturer"].map(norm)
        df["text"] = (df["t"] + " " + df["m"]).str.strip()
    return A, B, known


# ----------------------------------------------------------------------------
# BM25 (vectorized, matches rank_bm25.BM25Okapi to machine precision)
# ----------------------------------------------------------------------------
class BM25Corpus:
    """BM25 over a document corpus. The TF matrix / idf / doc lengths are built
    once; get_norm_scores(query, k1, b) recomputes only the saturation step, so
    a k1xb sweep reuses the index."""

    def __init__(self, corpus_texts):
        cv = CountVectorizer(tokenizer=str.split, token_pattern=None, lowercase=False)
        self.tf = cv.fit_transform(corpus_texts).tocsr().astype(np.float64)  # docs x terms
        self.vocab = cv.vocabulary_
        self.N = self.tf.shape[0]
        self.doc_len = np.asarray(self.tf.sum(axis=1)).ravel()
        self.avgdl = self.doc_len.mean() if self.N else 0.0
        # df per term, then rank_bm25 idf with epsilon floor for negatives
        df = np.asarray((self.tf > 0).sum(axis=0)).ravel().astype(np.float64)
        idf = np.log(self.N - df + 0.5) - np.log(df + 0.5)
        avg_idf = idf.mean() if idf.size else 0.0
        eps = 0.25 * avg_idf
        idf[idf < 0] = eps
        self.idf = idf

    def weight_matrix(self, k1, b):
        """Sparse docs x terms matrix W[d,t] = idf[t]*tf*(k1+1)/(tf+k1*(1-b+b*len[d]/avgdl))."""
        tf = self.tf
        rows = tf.tocoo()
        d = rows.row
        t = rows.col
        f = rows.data
        denom = f + k1 * (1.0 - b + b * self.doc_len[d] / self.avgdl)
        w = self.idf[t] * f * (k1 + 1.0) / denom
        return sp.csc_matrix((w, (d, t)), shape=tf.shape)

    def query_cols(self, query_text):
        cols = [self.vocab[tok] for tok in query_text.split() if tok in self.vocab]
        return cols  # repeats preserved -> repeated terms contribute multiple times


def _bm25_pair_scores(query_texts, targets_per_query, corpus, k1, b):
    """For each query index q with a list of target doc indices, return
    {(q, doc): normalized_score} where normalization divides by the query's max
    score over ALL docs (matches solution.py)."""
    W = corpus.weight_matrix(k1, b)  # docs x terms (csc)
    out = {}
    for q, targets in targets_per_query.items():
        cols = corpus.query_cols(query_texts[q])
        if not cols:
            for d in targets:
                out[(q, d)] = 0.0
            continue
        scores = np.asarray(W[:, cols].sum(axis=1)).ravel()  # length N docs
        mx = scores.max() or 1.0
        for d in targets:
            out[(q, d)] = scores[d] / mx
    return out


# ----------------------------------------------------------------------------
# pool + shared context
# ----------------------------------------------------------------------------
def _simmat(A, B, analyzer, ngram):
    vec = TfidfVectorizer(analyzer=analyzer, ngram_range=ngram, sublinear_tf=True)
    vec.fit(pd.concat([A["text"], B["text"]]))
    return (vec.transform(A["text"]) @ vec.transform(B["text"]).T).tocsr()


def _topk_per_A(sim, a_ids, b_ids, k):
    out = []
    for ia in range(sim.shape[0]):
        row = sim.getrow(ia)
        if row.nnz == 0:
            continue
        for j in np.argsort(-row.data)[:k]:
            out.append((int(a_ids[ia]), int(b_ids[row.indices[j]])))
    return out


def _topk_per_B(sim, a_ids, b_ids, k):
    simc = sim.tocsc()
    out = []
    for ib in range(simc.shape[1]):
        col = simc.getcol(ib)
        if col.nnz == 0:
            continue
        for j in np.argsort(-col.data)[:k]:
            out.append((int(a_ids[col.indices[j]]), int(b_ids[ib])))
    return out


def _rank_maps(sim):
    rank_a = {}
    simr = sim.tocsr()
    for ia in range(simr.shape[0]):
        row = simr.getrow(ia)
        if row.nnz == 0:
            continue
        for r, j in enumerate(np.argsort(-row.data)):
            rank_a[(ia, int(row.indices[j]))] = r
    rank_b = {}
    simc = sim.tocsc()
    for ib in range(simc.shape[1]):
        col = simc.getcol(ib)
        if col.nnz == 0:
            continue
        for r, j in enumerate(np.argsort(-col.data)):
            rank_b[(int(col.indices[j]), ib)] = r
    return rank_a, rank_b


def build_pool(A, B, known, ka=KA, kb=KB):
    a_ids = A["id"].to_numpy()
    b_ids = B["id"].to_numpy()
    aidx = {int(v): i for i, v in enumerate(a_ids)}
    bidx = {int(v): i for i, v in enumerate(b_ids)}

    Sc = _simmat(A, B, "char", (3, 4))
    Sw = _simmat(A, B, "word", (1, 2))
    Scw = _simmat(A, B, "char_wb", (2, 5))
    Sens = (Sc + Sw + Scw).tocsr()

    pool = sorted(
        set(_topk_per_A(Sens, a_ids, b_ids, ka))
        | set(_topk_per_B(Sens, a_ids, b_ids, kb))
        | set(known)
    )
    ra, rb = _rank_maps(Sens)

    # BM25 corpora (built once; reused across k1,b)
    bm_B = BM25Corpus(B["text"].tolist())  # docs = B, query = A
    bm_A = BM25Corpus(A["text"].tolist())  # docs = A, query = B
    pool_by_a = defaultdict(list)
    pool_by_b = defaultdict(list)
    for (ida, idb) in pool:
        pool_by_a[aidx[ida]].append(bidx[idb])
        pool_by_b[bidx[idb]].append(aidx[ida])

    return dict(
        A=A, B=B, known=known, pool=pool,
        a_ids=a_ids, b_ids=b_ids, aidx=aidx, bidx=bidx,
        Sc=Sc, Sw=Sw, Scw=Scw, Sens=Sens, ra=ra, rb=rb,
        bm_A=bm_A, bm_B=bm_B, pool_by_a=pool_by_a, pool_by_b=pool_by_b,
        a_text=A["text"].tolist(), b_text=B["text"].tolist(),
    )


# ----------------------------------------------------------------------------
# features
# ----------------------------------------------------------------------------
BASE_COLS = ["sc", "sw", "scw", "jac", "ra", "rb", "recip", "pdiff", "pclose",
             "pknown", "man_in", "lenr", "inter", "numi", "numj"]
BM25_COLS = ["bm25_ab", "bm25_ba", "bm25_max"]


def _nums(s):
    return set(re.findall(r"\d+\.?\d*", s))


def base_features(ctx):
    A, B = ctx["A"], ctx["B"]
    pool = ctx["pool"]
    aidx, bidx = ctx["aidx"], ctx["bidx"]
    Sc, Sw, Scw = ctx["Sc"], ctx["Sw"], ctx["Scw"]
    ra, rb = ctx["ra"], ctx["rb"]
    a_tok = [set(t.split()) for t in A["t"]]
    b_tok = [set(t.split()) for t in B["t"]]
    a_num = [_nums(t) for t in A["title"].astype(str)]
    b_num = [_nums(t) for t in B["title"].astype(str)]
    a_price = A["price"].to_numpy(dtype=float)
    b_price = B["price"].to_numpy(dtype=float)
    a_man = A["m"].tolist()
    b_text = B["text"].tolist()

    rows = []
    for (ida, idb) in pool:
        ia, ib = aidx[ida], bidx[idb]
        sc, sw, scw = Sc[ia, ib], Sw[ia, ib], Scw[ia, ib]
        ta, tb = a_tok[ia], b_tok[ib]
        inter = len(ta & tb)
        jac = inter / (len(ta | tb) or 1)
        ra_ = ra.get((ia, ib), 50)
        rb_ = rb.get((ia, ib), 50)
        recip = 1.0 / (1 + ra_) + 1.0 / (1 + rb_)
        pa, pb = a_price[ia], b_price[ib]
        if np.isnan(pa) or np.isnan(pb):
            pdiff, pclose, pknown = 1.0, 0.0, 0.0
        else:
            pdiff = abs(pa - pb) / (max(pa, pb) + 1)
            pclose = 1.0 if pdiff < 0.1 else 0.0
            pknown = 1.0
        man_in = 1.0 if a_man[ia] and (a_man[ia] in b_text[ib]) else 0.0
        lenr = min(len(ta), len(tb)) / (max(len(ta), len(tb)) or 1)
        na, nb = a_num[ia], b_num[ib]
        numi = len(na & nb)
        numj = len(na & nb) / (len(na | nb) or 1)
        rows.append([sc, sw, scw, jac, ra_, rb_, recip, pdiff, pclose, pknown,
                     man_in, lenr, inter, numi, numj])
    return np.array(rows, dtype=float), list(BASE_COLS)


def bm25_features(ctx, k1=1.5, b=0.75):
    pool = ctx["pool"]
    aidx, bidx = ctx["aidx"], ctx["bidx"]
    ab = _bm25_pair_scores(ctx["a_text"], ctx["pool_by_a"], ctx["bm_B"], k1, b)
    ba = _bm25_pair_scores(ctx["b_text"], ctx["pool_by_b"], ctx["bm_A"], k1, b)
    rows = []
    for (ida, idb) in pool:
        ia, ib = aidx[ida], bidx[idb]
        v_ab = ab.get((ia, ib), 0.0)
        v_ba = ba.get((ib, ia), 0.0)
        rows.append([v_ab, v_ba, max(v_ab, v_ba)])
    return np.array(rows, dtype=float), list(BM25_COLS)


# ----------------------------------------------------------------------------
# honest multi-seed CV
# ----------------------------------------------------------------------------
def _fit_score(Xs, pool, known, trainpos, heldout, C, pu):
    y = np.array([1 if p in trainpos else 0 for p in pool])
    mask = np.array([p not in heldout for p in pool])
    clf = LogisticRegression(max_iter=6000, class_weight="balanced", C=C)
    if pu is not None:
        sw = np.where(y == 1, 1.0, pu)
        clf.fit(Xs[mask], y[mask], sample_weight=sw[mask])
    else:
        clf.fit(Xs[mask], y[mask])
    return clf.decision_function(Xs)


def cv_recall(X, ctx, C=0.03, pu=0.03, seeds=range(20), nsplits=5, budget=BUDGET,
              scale=True):
    """Honest repeated k-fold CV: for each fold the held-out positives are removed
    from BOTH training and the returned top-`budget`; returns the per-fold
    recall@budget array."""
    pool = [tuple(p) for p in ctx["pool"]]
    known = set(ctx["known"])
    known_list = list(known)
    Xs = StandardScaler().fit_transform(X) if scale else X
    folds = []
    for seed in seeds:
        kf = KFold(n_splits=nsplits, shuffle=True, random_state=seed)
        for tr, te in kf.split(known_list):
            heldout = set(known_list[i] for i in te)
            trainpos = set(known_list[i] for i in tr)
            s = _fit_score(Xs, pool, known, trainpos, heldout, C, pu)
            order = np.argsort(-s)
            chosen = []
            for i in order:
                p = pool[i]
                if p in trainpos:
                    continue
                chosen.append(p)
                if len(chosen) >= budget:
                    break
            folds.append(len(set(chosen) & heldout) / len(heldout))
    return np.array(folds)


def cv_perpair(X, ctx, C=0.03, pu=0.03, seeds=range(20), nsplits=5, budget=BUDGET,
               scale=True):
    """Like cv_recall but tracks, per known pair, how often it was missed and its
    rank in the model's full ranked pool across the folds where it was held out.
    Returns {pair: {"trials", "misses", "ranks":[...]}}."""
    pool = [tuple(p) for p in ctx["pool"]]
    known = set(ctx["known"])
    known_list = list(known)
    Xs = StandardScaler().fit_transform(X) if scale else X
    stats = {p: {"trials": 0, "misses": 0, "ranks": []} for p in known}
    for seed in seeds:
        kf = KFold(n_splits=nsplits, shuffle=True, random_state=seed)
        for tr, te in kf.split(known_list):
            heldout = set(known_list[i] for i in te)
            trainpos = set(known_list[i] for i in tr)
            s = _fit_score(Xs, pool, known, trainpos, heldout, C, pu)
            order = np.argsort(-s)
            # rank of each pool pair among the retained candidates (train pos removed)
            rank_of = {}
            chosen_set = set()
            r = 0
            for i in order:
                p = pool[i]
                if p in trainpos:
                    continue
                rank_of[p] = r
                if r < budget:
                    chosen_set.add(p)
                r += 1
            for p in heldout:
                st = stats[p]
                st["trials"] += 1
                st["ranks"].append(rank_of.get(p, 10 ** 9))
                if p not in chosen_set:
                    st["misses"] += 1
    return stats


if __name__ == "__main__":
    A, B, known = load_tables()
    ctx = build_pool(A, B, known)
    print("pool", len(ctx["pool"]),
          "ceiling", len(set(ctx["pool"]) & known) / len(known))
    Xb, cb = base_features(ctx)
    Xm, cm = bm25_features(ctx, 1.5, 0.75)
    X = np.hstack([Xb, Xm])
    r = cv_recall(X, ctx, seeds=range(5))
    print("base+bm25(1.5,0.75) 5-seed CV:", round(r.mean(), 4), "+/-", round(r.std(), 4))
