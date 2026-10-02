import math
from collections import defaultdict
from hw3_utils import parse_documents_or_queries, parse_collection_stats, output_xml

def compute_dmm_p_w_Md(tf_d, doc_len, V_F_size, delta=0.1):
    """
    Compute smoothed p(w|M_d) for all terms in a doc using the DMM formula.
    """
    p_w_Md = {}
    for term in tf_d:
        tf = tf_d[term]
        p_w_Md[term] = (tf + delta) / (doc_len + delta * V_F_size)
    return p_w_Md

def compute_dmm_feedback_model(docs_tfs, docs_len, cf_dict, total_terms_corpus, delta, lam, V_F_size):
    """
    Compute p(w|M_F) using DMM with per-query feedback vocabulary size (V_F_size).
    """
    feedback_vocab = set()
    for tf_d in docs_tfs.values():
        feedback_vocab.update(tf_d.keys())

    # Step 1: Compute p(w|M_d) for each doc
    doc_models = []
    for doc_id, tf_d in docs_tfs.items():
        doc_len = docs_len[doc_id]
        p_w_md = compute_dmm_p_w_Md(tf_d, doc_len, V_F_size, delta)
        doc_models.append((p_w_md, docs_len[doc_id]))


    # Step 2: Compute geometric mean (centroid) and subtract KL penalty with background model
    p_w_MF = {}
    for w in feedback_vocab:
        log_sum = 0.0
        for p_w_md, doc_len in doc_models:
            prob = p_w_md.get(w, delta / (doc_len + delta * V_F_size))
            log_sum += math.log(prob)
        centroid = log_sum / len(doc_models)

        # Collection probability
        cf = cf_dict.get(w, 0)
        p_w_Mc = cf / total_terms_corpus if total_terms_corpus > 0 else 1e-12

        # Final DMM formula
        score = math.exp((1 / (1 - lam)) * (centroid - lam * math.log(p_w_Mc)))
        p_w_MF[w] = score

    # Term Clipping
    total = sum(p_w_MF.values())
    for w in p_w_MF:
        p_w_MF[w] /= total

    return p_w_MF

def top_k_terms(p_w, k=25):
    top_items = sorted(p_w.items(), key=lambda x: x[1], reverse=True)[:k]
    total = sum(w for _, w in top_items)
    if total == 0:
        return dict(top_items)  # Avoid division by zero
    return {t: w / total for t, w in top_items}

def combine_with_query_model(p_w_Q, p_w_MF, lam=0.5):
    all_terms = set(p_w_Q) | set(p_w_MF)
    p_final = {}
    for w in all_terms:
        p_q = p_w_Q.get(w, 0)
        p_r = p_w_MF.get(w, 0)
        p_final[w] = lam * p_q + (1 - lam) * p_r
    return {t: w for t, w in p_final.items() if w > 0}

# --------------------------
# Main DMM Execution

#cf_dict, total_terms_corpus = parse_collection_stats("./gov2_collection_stats.csv")
queries_tfs, queries_len = parse_documents_or_queries("q_stemmed.tsv")

cf_dict, total_terms_corpus = parse_collection_stats("/data/HW3/gov2_collection_stats.csv")


all_queries_models = {}

for qid, q_tf in queries_tfs.items():
    total_q_len = queries_len[qid]
    p_w_Q = {term: tf / total_q_len for term, tf in q_tf.items()}

    # Load feedback documents for this query
   # docs_tfs, docs_len = parse_documents_or_queries(f"./feedback_docs/{qid}.tsv")
    docs_tfs, docs_len = parse_documents_or_queries(f"/home/student/HW3/feedback_docs/{qid}.tsv")

    # Compute V_F (distinct terms in feedback set)
    feedback_vocab = set()
    for tf_d in docs_tfs.values():
        feedback_vocab.update(tf_d.keys())
    V_F_size = len(feedback_vocab)

    # Compute DMM feedback model
    p_w_MF = compute_dmm_feedback_model(
        docs_tfs, docs_len,
        cf_dict, total_terms_corpus,
        delta=0.1, lam=0.1,
        V_F_size=V_F_size
    )

    # Select top 25 terms from feedback model
    p_w_MF_top = top_k_terms(p_w_MF, k=25)

    # Combine with original query (anchoring)
    p_final = combine_with_query_model(p_w_Q, p_w_MF_top, lam=0.5)

    # Save final model for this query
    all_queries_models[qid] = dict(sorted(p_final.items(), key=lambda item: item[1], reverse=True))

# Output the final XML file for Indri
output_xml(all_queries_models, "dmm.xml")
