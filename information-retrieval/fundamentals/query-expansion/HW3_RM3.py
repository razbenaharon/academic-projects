from hw3_utils import parse_documents_or_queries, parse_collection_stats, output_xml
from collections import defaultdict


def compute_mle_p_w_given_Md(tf_d, doc_len, term):
    """
    Compute p(w|M_d) for each term in document d using mle
    """
    tf_w_d = tf_d.get(term, 0)
    return tf_w_d/doc_len


def calc_p_q_given_md(tf_d, doc_len, cf_dict, total_terms_corpus,query ,mu=1000):
    """
    Compute p(w|M_d) for each term in document d using Dirichlet smoothing.
    """
    p_q_given_md=1
    p_w_md={}
    for term in query:
        cf_w = cf_dict.get(term, 0)
        p_mle_w_given_mc = cf_w / total_terms_corpus
        tf_w_d = tf_d.get(term, 0)
        p_w_md[term] = (tf_w_d + mu * p_mle_w_given_mc) / (doc_len + mu)
        p_q_given_md *= p_w_md[term]

    return p_q_given_md


def compute_p_w_given_R(docs_tfs, docs_len, cf_dict, total_terms_corpus,query,mu=1000):
    """
    Compute p(w|R) = sum_d [ p(w|M_d) * p(d|Q) ]
    Assuming uniform p(d|Q) over feedback documents.
    """
    p_w_R = defaultdict(float)
    p_q_given_md_i = {}
    for doc_id, tf_d in docs_tfs.items():
        doc_len = docs_len[doc_id]
        p_q_given_md_i[doc_id]=calc_p_q_given_md(tf_d, doc_len, cf_dict, total_terms_corpus,query, mu)
    sum_p_md_q = sum(p_q_given_md_i.values())

    for doc_id, tf_d in docs_tfs.items():
        doc_len = docs_len[doc_id]
        for term in tf_d.keys():
            p_w_md = compute_mle_p_w_given_Md(tf_d, doc_len,term)
            p_w_R[term] += p_q_given_md_i[doc_id] * p_w_md /sum_p_md_q

    return dict(p_w_R)


def top_k_terms(p_w_R, k=25):
    """
    Select top-k terms with highest probabilities from p(w|R),
    and normalize them so the total sums to 1.
    """
    sorted_terms = sorted(p_w_R.items(), key=lambda x: x[1], reverse=True)[:k]
    total = sum(w for _, w in sorted_terms)
    if total == 0:
        return dict(sorted_terms)  # Avoid division by zero
    return {term: weight / total for term, weight in sorted_terms}


def combine_rm3(p_w_Q, p_w_R, lam=0.5):
    """
    Combine original query model p(w|Q) with relevance model p(w|R).
    """
    terms = set(p_w_Q.keys()).union(set(p_w_R.keys()))
    p_final = {}
    for term in terms:
        p_q = p_w_Q.get(term, 0.0)
        p_r = p_w_R.get(term, 0.0)
        p_final[term] =lam * p_q + (1 - lam) * p_r
    p_final = {t: w for t, w in p_final.items() if w > 0}
    return p_final


# Load collection statistics
cf_dict, total_terms_corpus = parse_collection_stats("/data/HW3/gov2_collection_stats.csv")
#cf_dict, total_terms_corpus = parse_collection_stats("C:/Users/User/Desktop/IR3/gov2_collection_stats.csv")
# Load original queries (tokenized and stemmed)
queries_tfs, queries_len = parse_documents_or_queries("q_stemmed.tsv")

all_queries_models = {}

for qid, q_tf in queries_tfs.items():
    # Compute p(w|Q)
    total_q_len = queries_len[qid]
    p_w_Q = {term: tf / total_q_len for term, tf in q_tf.items()}

    # Load feedback documents for this query
    docs_tfs, docs_len = parse_documents_or_queries(f"/home/student/HW3/feedback_docs/{qid}.tsv")
    #docs_tfs, docs_len = parse_documents_or_queries(f"C:/Users/User/Desktop/IR3/feedback_docs/{qid}.tsv")

    # Compute p(w|R) using Dirichlet smoothing
    d = dict(q_tf.items())
    # Step 2: Get all keys
    keys = list(d.keys())
    p_w_R = compute_p_w_given_R(docs_tfs, docs_len, cf_dict, total_terms_corpus, keys ,mu=1000)

    # Select top 25 terms from p(w|R)
    p_w_R_top = top_k_terms(p_w_R, k=25)

    # Combine original query with RM3 relevance model
    p_final = combine_rm3(p_w_Q, p_w_R_top, lam=0.5)
    p_final_sorted = dict(sorted(p_final.items(), key=lambda item: item[1], reverse=True))

    all_queries_models[qid] = p_final_sorted


# Write Indri weighted queries XML file
output_xml(all_queries_models, "rm3.xml")