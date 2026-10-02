"""
Task 3 (execution) — LOCAL, no-API enrichment.

Per the user's decision, the enrichment is produced locally (no LLM API, no key,
no cost) by a deterministic rule-based enricher that encodes the same knowledge
an LLM would supply. For every row of tableA and tableB it emits the three
requested columns and caches them keyed by row id:

    standardized_brand : canonical brand token ("adobe systems"/"adobe corp" -> "adobe")
    clean_version      : list of version / edition / year tokens (["cs3"], ["6.0"], ["2007"])
    product_category   : one of {Software, Hardware, Books, Music, Games, Other}

Outputs enrich_A.json / enrich_B.json. See llm_enrichment_design.md for the
drop-in LLM (Batch-API) version of exactly these columns.
"""
import re
import json
import pandas as pd

import em_core as C

# corporate / generic tokens stripped when reducing a manufacturer to its brand
CORP_SUFFIX = {"inc", "corp", "corporation", "ltd", "llc", "co", "llp", "gmbh",
               "sa", "ag", "plc", "lp"}
GENERIC = {"software", "technologies", "technology", "systems", "system",
           "international", "intl", "group", "publishing", "publisher",
           "entertainment", "interactive", "media", "multimedia",
           "communications", "productions", "worldwide", "usa", "america",
           "north", "the", "of", "and", "a", "s"}

# a few explicit canonicalizations for frequent multi-token brands where the
# first-token rule alone would split variants
BRAND_ALIAS = {
    "ca": "computer associates",
    "hp": "hewlett packard",
    "hewlett": "hewlett packard",
}

EDITIONS = {"professional", "standard", "premium", "deluxe", "ultimate",
            "enterprise", "home", "student", "basic", "pro", "academic",
            "upgrade", "edition", "suite", "collectors", "special"}

CATEGORY_KEYWORDS = {
    "Games": ["game", "games", "gaming", "xbox", "playstation", "ps2", "ps3",
              "wii", "nintendo", "gamecube", "rpg", "arcade", "sims", "poker",
              "chess", "puzzle", "adventure"],
    "Books": ["book", "books", "guide", "manual", "encyclopedia", "dictionary",
              "dummies", "handbook", "reference", "cookbook", "workbook"],
    "Music": ["music", "audio", "mp3", "soundtrack", "karaoke", "singing",
              "song", "songs", "band", "guitar", "piano", "dj", "mixing"],
    "Hardware": ["drive", "printer", "scanner", "router", "cable", "adapter",
                 "keyboard", "mouse", "monitor", "webcam", "headset", "usb",
                 "hardware", "device", "modem", "server rack", "battery"],
    "Software": ["software", "windows", "mac", "cd-rom", "cdrom", "license",
                 "licence", "upgrade", "edition", "suite", "antivirus",
                 "office", "version", "oem", "app", "application", "utility",
                 "accounting", "database", "photoshop", "quickbooks", "os"],
}


STOP = {"the", "of", "and", "a", "s", "for", "with", "new", "inc", "co"}


def canonical_brand(manuf_norm):
    """Reduce a normalized manufacturer string to a single canonical brand token."""
    if not manuf_norm:
        return ""
    toks = [t for t in manuf_norm.split() if t]
    # drop trailing corporate suffixes / generic descriptors
    while toks and (toks[-1] in CORP_SUFFIX or toks[-1] in GENERIC):
        toks.pop()
    # drop leading generic descriptors ("the", "new", ...)
    while toks and (toks[0] in GENERIC or toks[0] in STOP):
        toks.pop(0)
    if not toks:
        return ""
    brand = toks[0]
    if brand in STOP:
        return ""
    return BRAND_ALIAS.get(brand, brand)


def build_brand_vocab(A):
    vocab = set()
    for m in A["m"]:
        b = canonical_brand(m)
        if len(b) >= 3:
            vocab.add(b)
    return vocab


def extract_versions(title):
    s = str(title).lower()
    out = set()
    out |= {v for v in re.findall(r"\b\d+\.\d+\b", s)}                 # 6.0, 7.5
    out |= {re.sub(r"\s+", "", v) for v in re.findall(r"\bcs\s?\d+\b", s)}   # cs3, cs 3
    out |= {re.sub(r"\s+", "", v) for v in re.findall(r"\bv\s?\d+(?:\.\d+)?\b", s)}  # v6, v6.0
    out |= {y for y in re.findall(r"\b(?:19|20)\d{2}\b", s)}           # years
    toks = set(re.findall(r"[a-z0-9]+", s))
    out |= (toks & EDITIONS)                                           # edition words
    return sorted(out)


def categorize(title, brand):
    s = (str(title) + " " + brand).lower()
    toks = set(re.findall(r"[a-z0-9\-]+", s))
    best, best_score = "Other", 0
    for cat, kws in CATEGORY_KEYWORDS.items():
        # multi-word keywords match as substrings; single words match whole tokens
        # (so "book" does not match inside "quickbooks")
        score = sum(1 for kw in kws if (kw in s if " " in kw else kw in toks))
        if score > best_score:
            best, best_score = cat, score
    # domain prior: Amazon/Google *software products* -> default to Software
    if best_score == 0:
        return "Software"
    return best


def enrich_table(df, brand_vocab, is_A):
    out = {}
    for _, row in df.iterrows():
        rid = int(row["id"])
        m_norm = row["m"]
        brand = canonical_brand(m_norm)
        if (not brand) and (not is_A):
            # Table B: manufacturer usually missing -> recover brand from the title
            for tok in row["t"].split():
                if tok in brand_vocab:
                    brand = tok
                    break
        versions = extract_versions(row["title"])
        category = categorize(row["title"], brand)
        out[rid] = {
            "standardized_brand": brand,
            "clean_version": versions,
            "product_category": category,
        }
    return out


def main():
    A, B, _ = C.load_tables()
    brand_vocab = build_brand_vocab(A)
    enrA = enrich_table(A, brand_vocab, is_A=True)
    enrB = enrich_table(B, brand_vocab, is_A=False)

    with open(C.BASE + "enrich_A.json", "w") as f:
        json.dump(enrA, f)
    with open(C.BASE + "enrich_B.json", "w") as f:
        json.dump(enrB, f)

    def cov(enr):
        n = len(enr)
        brand = sum(1 for v in enr.values() if v["standardized_brand"])
        ver = sum(1 for v in enr.values() if v["clean_version"])
        return n, brand / n, ver / n

    for name, enr in [("A", enrA), ("B", enrB)]:
        n, bc, vc = cov(enr)
        cats = pd.Series([v["product_category"] for v in enr.values()]).value_counts()
        print(f"[{name}] rows={n}  brand_coverage={bc:.1%}  version_coverage={vc:.1%}")
        print(f"     categories: {dict(cats)}")
    print(f"\nbrand vocabulary size: {len(brand_vocab)}")
    print("Saved enrich_A.json, enrich_B.json")
    # sample
    print("\nsamples (A):")
    for rid in list(enrA)[:4]:
        print(f"  A{rid}: {A[A['id']==rid]['title'].iloc[0][:55]!r} -> {enrA[rid]}")
    print("samples (B):")
    for rid in list(enrB)[:4]:
        print(f"  B{rid}: {B[B['id']==rid]['title'].iloc[0][:55]!r} -> {enrB[rid]}")


if __name__ == "__main__":
    main()
