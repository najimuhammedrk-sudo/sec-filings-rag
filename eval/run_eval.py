import json
import sys
sys.path.insert(0, "src")
import chromadb
from sentence_transformers import SentenceTransformer
from route import route, build_where

K = 5

EVIDENCE = {
    "q01": ["limited sources of supply", "sole source providers"],
    "q02": ["EU AI Act"],
    "q03": ["threat actors are using and exploiting"],
    "q04": ["Microsoft, Oracle, SAP, Salesforce and Workday"],
    "q05": ["41,525", "41.5 billion"],
    "q06": ["23,769"],
    "q07": ["28.1 billion", "28,101"],
}
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

MODES = ["filtered", "routed", "unfiltered"]
model = SentenceTransformer("all-MiniLM-L6-v2")
client = chromadb.PersistentClient(path="data/chroma")
cols = {n: client.get_collection(n) for n in ("fixed", "section")}
qs = json.load(open("eval/questions.json", encoding="utf-8"))


def where_for(company, period):
    return {"$and": [{"company": company}, {"period": period}]}


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
    tick, pers = route(q["question"])
    print(f"{q['id']:<5}routed -> {tick} {pers}")
    for mode in MODES:
        if mode == "filtered":
            w_single = where_for(q["company"], q["period"])
        elif mode == "routed":
            w_single = build_where(tick, pers)
        else:
            w_single = None
        for name, col in cols.items():
            b = res[(mode, name)]
            if q["type"] == "unanswerable":
                _, _, dists = query(col, emb, w_single)
                b["unans"].append((q["id"], round(dists[0], 3)))
            elif q["id"] in CROSS:
                ranks = []
                for per, terms in CROSS[q["id"]].items():
                    split = mode == "filtered" or (
                        mode == "routed" and tick == q["company"] and per in pers)
                    w = where_for(q["company"], per) if split else w_single
                    docs, metas, _ = query(col, emb, w)
                    ranks.append(first_rank(docs, metas, terms, q["company"], per))
                rank = None if any(r is None for r in ranks) else max(ranks)
                b["cross"].append(rank)
                print(f"{q['id']:<5}{mode:<11}{name:<9}{rank or 'miss'} {ranks}")
            elif q["id"] in EVIDENCE:
                docs, metas, _ = query(col, emb, w_single)
                rank = first_rank(docs, metas, EVIDENCE[q["id"]], q["company"], q["period"])
                b["single"].append(rank)
                print(f"{q['id']:<5}{mode:<11}{name:<9}{rank or 'miss'}")


def tally(ranks):
    return ", ".join(f"{sum(1 for r in ranks if r and r <= k)}/{len(ranks)}" for k in (1, 3, 5))


print("\n=== SUMMARY (hit@1, hit@3, hit@5) ===")
for (mode, name), b in res.items():
    allr = b["single"] + b["cross"]
    print(f"{mode:<11}{name:<9} all {tally(allr)} | single {tally(b['single'])} | cross {tally(b['cross'])}")

print("\n=== UNANSWERABLE best distance ===")
for (mode, name), b in res.items():
    print(f"{mode:<11}{name:<9}", b["unans"])