import json
import chromadb
from sentence_transformers import SentenceTransformer

K = 5

# single-filing questions: a chunk is a hit if it contains ANY of these strings
EVIDENCE = {
    "q01": ["limited sources of supply", "sole source providers"],
    "q02": ["EU AI Act"],
    "q03": ["threat actors are using and exploiting"],
    "q04": ["Microsoft, Oracle, SAP, Salesforce and Workday"],
    "q05": ["41,525", "41.5 billion"],
    "q06": ["23,769"],
    "q07": ["28.1 billion", "28,101"],
}

# cross-year questions: evidence per period; BOTH periods must be retrieved
CROSS = {
    "q08": {"2026-05-31": ["if we incur costs higher than expected"],
            "2025-05-31": ["expect to continue to invest significant resources"]},
    "q09": {"2026-07-31": ["single system of intelligence"],
            "2025-07-31": ["virtual team of AI agents"]},
    "q14": {"2026-01-31": ["threat actors are using and exploiting"],
            "2025-01-31": ["and our Salesforce Platform present"]},
    "q15": {"2026-06-30": ["gross margin percentage decreased to 66%"],
            "2025-06-30": ["gross margin percentage decreased to 69%"]},
}

MODES = ["filtered", "unfiltered"]
model = SentenceTransformer("all-MiniLM-L6-v2")
client = chromadb.PersistentClient(path="data/chroma")
cols = {n: client.get_collection(n) for n in ("fixed", "section")}
qs = json.load(open("eval/questions.json", encoding="utf-8"))


def where_for(q, period):
    return {"$and": [{"company": q["company"]}, {"period": period}]}


def query(col, emb, where):
    kw = dict(query_embeddings=emb, n_results=K,
              include=["documents", "metadatas", "distances"])
    if where:
        kw["where"] = where
    r = col.query(**kw)
    return r["documents"][0], r["metadatas"][0], r["distances"][0]


def first_rank(docs, metas, terms, company, period):
    for i, (d, m) in enumerate(zip(docs, metas)):
        if m["company"] == company and m["period"] == period and any(t in d for t in terms):
            return i + 1
    return None


res = {(m, n): {"single": [], "cross": [], "unans": []} for m in MODES for n in cols}

for q in qs:
    emb = model.encode([q["question"]]).tolist()
    for mode in MODES:
        for name, col in cols.items():
            bucket = res[(mode, name)]
            if q["type"] == "unanswerable":
                w = where_for(q, q["period"]) if mode == "filtered" else None
                _, _, dists = query(col, emb, w)
                bucket["unans"].append((q["id"], round(dists[0], 3)))
                print(f"{q['id']:<5}{mode:<11}{name:<9}best distance {dists[0]:.3f}")
            elif q["id"] in CROSS:
                ranks = []
                if mode == "filtered":
                    for per, terms in CROSS[q["id"]].items():
                        docs, metas, _ = query(col, emb, where_for(q, per))
                        ranks.append(first_rank(docs, metas, terms, q["company"], per))
                else:
                    docs, metas, _ = query(col, emb, None)
                    for per, terms in CROSS[q["id"]].items():
                        ranks.append(first_rank(docs, metas, terms, q["company"], per))
                rank = None if any(r is None for r in ranks) else max(ranks)
                bucket["cross"].append(rank)
                print(f"{q['id']:<5}{mode:<11}{name:<9}{rank or 'miss'}  (per-period {ranks})")
            elif q["id"] in EVIDENCE:
                w = where_for(q, q["period"]) if mode == "filtered" else None
                docs, metas, _ = query(col, emb, w)
                rank = first_rank(docs, metas, EVIDENCE[q["id"]], q["company"], q["period"])
                bucket["single"].append(rank)
                print(f"{q['id']:<5}{mode:<11}{name:<9}{rank or 'miss'}")


def tally(ranks):
    return ", ".join(f"{sum(1 for r in ranks if r and r <= k)}/{len(ranks)}" for k in (1, 3, 5))


print("\n=== SUMMARY (hit@1, hit@3, hit@5) ===")
for (mode, name), b in res.items():
    allr = b["single"] + b["cross"]
    print(f"{mode:<11}{name:<9} all {tally(allr)} | single {tally(b['single'])} | cross {tally(b['cross'])}")

print("\n=== UNANSWERABLE: best distance per question ===")
for (mode, name), b in res.items():
    print(f"{mode:<11}{name:<9}", b["unans"])

print("\n=== ROWS FOR results_log.md (fill in the run number and change) ===")
for (mode, name), b in res.items():
    allr = b["single"] + b["cross"]
    print(f"| N | {mode}, {name} | {tally(allr)} |")