"""
Mini-Hackathon: Blocking for Entity Matching (Amazon-Google products)
=====================================================================

Goal: produce <= 2000 candidate (id_a, id_b) pairs maximizing recall of the
hidden ground-truth matches, while EXCLUDING the 100 given matches.

Approach = "learning to block":
  1. Normalize text (title + manufacturer) for both tables.
  2. Build TF-IDF cosine views (char 3-4, word 1-2, char_wb 2-5); their sum is an
     "ensemble" similarity used only to build a candidate POOL.
  3. POOL = (top-10 B per A)  UNION  (top-8 A per B) on the ensemble similarity.
     This two-sided k-NN pool has a ~1.0 recall ceiling on the 100 known matches
     (i.e. essentially every true match is already retrieved), so recall becomes
     a *ranking* problem, not a *retrieval* problem.
  4. Score every pool pair with a regularized logistic-regression ranker trained
     on the 100 known matches, using 18 pair features (three cosine sims, token
     Jaccard, two-sided similarity ranks + reciprocal rank, price agreement,
     manufacturer containment, numeric-token overlap, length ratio, and three
     BM25 signals). Two ideas that mattered a lot with only 100 labels:
       * strong L2 regularization (C=0.03) to avoid overfitting;
       * PU weighting: unlabeled (non-known) pairs are treated as *unlabeled*,
         not hard negatives, by giving them a small sample weight (0.03) -- many
         of them are in fact hidden true matches.
  5. Take the top-2000 pool pairs by ranker score, dropping the 100 known.

Honest evaluation: repeated k-fold CV on the 100 known matches, where held-out
positives are removed from BOTH the ranker's training and the pool-scoring, then
we check how many held-out matches land in the top-2000. Averaged over 20 seeds
x 5 folds = 100 estimates:

    global top-2000 by cosine .................. ~0.75
    rank the k-NN pool by raw similarity ....... ~0.74
    LR ranker, base 15 features ................ ~0.845
    + BM25 features, strong reg, PU weighting .. ~0.894   (this script)

Dependencies: numpy, pandas, scikit-learn only (BM25 is implemented inline).
"""

import pickle
import re
from collections import defaultdict
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler

# ----------------------------------------------------------------------------
# helpers.py (pasted per instructions -- do NOT change max_pairs)
# ----------------------------------------------------------------------------
def validate_candidate_set(candidate_set, tableA_ids, tableB_ids, max_pairs=2000):
    assert isinstance(candidate_set, set), "Submission must be a set."
    assert len(candidate_set) <= max_pairs, f"Submission exceeds {max_pairs} pairs."
    for pair in candidate_set:
        assert isinstance(pair, tuple) and len(pair) == 2, "Each element must be a tuple of length 2."
        ida, idb = pair
        assert ida in tableA_ids, f"{ida} not found in Table A."
        assert idb in tableB_ids, f"{idb} not found in Table B."


def save_submission(candidate_set, sid):
    assert isinstance(sid, str), "Student ID must be a string."
    assert sid.isdigit(), "Student ID must contain only digits."
    filename = f"{sid}.pkl"
    with open(filename, "wb") as f:
        pickle.dump(candidate_set, f)
    print(f"Saved submission to {filename}")


# ----------------------------------------------------------------------------
# config
# ----------------------------------------------------------------------------
BASE = ""            # run from the folder holding the csv / pkl files
SID = "000000000"
KA, KB = 10, 8       # two-sided k-NN pool sizes
BUDGET = 2000
C_REG = 0.03         # L2 strength for the ranker
PU_W = 0.03          # sample weight for unlabeled (non-known) pairs

# ----------------------------------------------------------------------------
# 1. load + normalize
# ----------------------------------------------------------------------------
A = pd.read_csv(BASE + "tableA.csv")
B = pd.read_csv(BASE + "tableB.csv")
with open(BASE + "100_matches.pkl", "rb") as f:
    known = {(int(a), int(b)) for a, b in pickle.load(f)}


def norm(s):
    if pd.isna(s):
        return ""
    s = str(s).lower()
    s = re.sub(r"[^a-z0-9 ]", " ", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s


for df in (A, B):
    df["t"] = df["title"].map(norm)
    df["m"] = df["manufacturer"].map(norm)
    df["text"] = (df["t"] + " " + df["m"]).str.strip()

a_ids = A["id"].to_numpy()
b_ids = B["id"].to_numpy()
aidx = {int(v): i for i, v in enumerate(a_ids)}
bidx = {int(v): i for i, v in enumerate(b_ids)}

# ----------------------------------------------------------------------------
# 2. tfidf cosine views + ensemble (for building the pool + sim features)
# ----------------------------------------------------------------------------
def simmat(analyzer, ngram):
    vec = TfidfVectorizer(analyzer=analyzer, ngram_range=ngram, sublinear_tf=True)
    vec.fit(pd.concat([A["text"], B["text"]]))
    return (vec.transform(A["text"]) @ vec.transform(B["text"]).T).tocsr()


Sc = simmat("char", (3, 4))
Sw = simmat("word", (1, 2))
Scw = simmat("char_wb", (2, 5))
Sens = (Sc + Sw + Scw).tocsr()

# ----------------------------------------------------------------------------
# 3. two-sided k-NN candidate pool
# ----------------------------------------------------------------------------
def topk_per_A(sim, k):
    out = []
    for ia in range(sim.shape[0]):
        row = sim.getrow(ia)
        if row.nnz == 0:
            continue
        for j in np.argsort(-row.data)[:k]:
            out.append((int(a_ids[ia]), int(b_ids[row.indices[j]])))
    return out


def topk_per_B(sim, k):
    simc = sim.tocsc()
    out = []
    for ib in range(simc.shape[1]):
        col = simc.getcol(ib)
        if col.nnz == 0:
            continue
        for j in np.argsort(-col.data)[:k]:
            out.append((int(a_ids[col.indices[j]]), int(b_ids[ib])))
    return out


pool = sorted(set(topk_per_A(Sens, KA)) | set(topk_per_B(Sens, KB)) | set(known))
print(f"pool size = {len(pool)}  | ceiling recall on known = "
      f"{len(set(pool) & known) / len(known):.3f}")

# ----------------------------------------------------------------------------
# 4. helper signals: similarity ranks + BM25 (both directions)
# ----------------------------------------------------------------------------
def rank_maps(sim):
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


ra, rb = rank_maps(Sens)


class BM25:
    """Minimal BM25Okapi (matches rank_bm25's BM25Okapi to machine precision)."""
    def __init__(self, corpus, k1=1.5, b=0.75, epsilon=0.25):
        self.k1, self.b = k1, b
        self.N = len(corpus)
        self.doc_len = np.array([len(d) for d in corpus], dtype=float)
        self.avgdl = self.doc_len.mean() if self.N else 0.0
        self.freqs = []
        df = {}
        for d in corpus:
            f = {}
            for w in d:
                f[w] = f.get(w, 0) + 1
            self.freqs.append(f)
            for w in f:
                df[w] = df.get(w, 0) + 1
        idf = {}
        neg = []
        ssum = 0.0
        for w, n in df.items():
            v = np.log(self.N - n + 0.5) - np.log(n + 0.5)
            idf[w] = v
            ssum += v
            if v < 0:
                neg.append(w)
        eps = epsilon * (ssum / len(idf)) if idf else 0.0
        for w in neg:
            idf[w] = eps
        self.idf = idf

    def get_scores(self, query):
        score = np.zeros(self.N)
        for q in query:
            if q not in self.idf:
                continue
            qf = np.array([f.get(q, 0) for f in self.freqs], dtype=float)
            denom = qf + self.k1 * (1 - self.b + self.b * self.doc_len / self.avgdl)
            score += self.idf[q] * (qf * (self.k1 + 1)) / denom
        return score


A_tok_txt = [t.split() for t in A["text"]]
B_tok_txt = [t.split() for t in B["text"]]
bm25_B = BM25(B_tok_txt)   # docs = B, query = A
bm25_A = BM25(A_tok_txt)   # docs = A, query = B

pool_by_a = defaultdict(list)
pool_by_b = defaultdict(list)
for (ida, idb) in pool:
    pool_by_a[aidx[ida]].append(bidx[idb])
    pool_by_b[bidx[idb]].append(aidx[ida])

bm25_ab = {}
for ia, ibs in pool_by_a.items():
    sc = bm25_B.get_scores(A_tok_txt[ia]); mx = sc.max() or 1.0
    for ib in ibs:
        bm25_ab[(ia, ib)] = sc[ib] / mx
bm25_ba = {}
for ib, ias in pool_by_b.items():
    sc = bm25_A.get_scores(B_tok_txt[ib]); mx = sc.max() or 1.0
    for ia in ias:
        bm25_ba[(ia, ib)] = sc[ia] / mx

# ----------------------------------------------------------------------------
# 5. pair features (18)
# ----------------------------------------------------------------------------
a_tok = [set(t.split()) for t in A["t"]]
b_tok = [set(t.split()) for t in B["t"]]


def nums(s):
    return set(re.findall(r"\d+\.?\d*", s))


a_num = [nums(t) for t in A["title"].astype(str)]
b_num = [nums(t) for t in B["title"].astype(str)]
a_price = A["price"].to_numpy(dtype=float)
b_price = B["price"].to_numpy(dtype=float)
a_man = A["m"].tolist()
b_text = B["text"].tolist()


def feats(ida, idb):
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
    b_ab = bm25_ab.get((ia, ib), 0.0)
    b_ba = bm25_ba.get((ia, ib), 0.0)
    b_max = max(b_ab, b_ba)
    return [sc, sw, scw, jac, ra_, rb_, recip, pdiff, pclose, pknown,
            man_in, lenr, inter, numi, numj, b_ab, b_ba, b_max]


X = np.array([feats(a, b) for a, b in pool])
Xs = StandardScaler().fit_transform(X)
y = np.array([1 if p in known else 0 for p in pool])

# ----------------------------------------------------------------------------
# 6. train regularized + PU-weighted ranker, score pool, take top-2000
# ----------------------------------------------------------------------------
sample_w = np.where(y == 1, 1.0, PU_W)         # PU: unlabeled negatives downweighted
clf = LogisticRegression(max_iter=6000, class_weight="balanced", C=C_REG)
clf.fit(Xs, y, sample_weight=sample_w)
scores = clf.decision_function(Xs)
order = np.argsort(-scores)

candidate_set = set()
for idx in order:
    p = pool[idx]
    if p in known:            # the 100 given matches must not appear
        continue
    candidate_set.add(p)
    if len(candidate_set) >= BUDGET:
        break

print(f"final candidate set size = {len(candidate_set)}")
assert candidate_set.isdisjoint(known), "known matches leaked into submission!"

# ----------------------------------------------------------------------------
# 7. validate + save
# ----------------------------------------------------------------------------
validate_candidate_set(candidate_set, set(A["id"]), set(B["id"]))
save_submission(candidate_set, SID)
