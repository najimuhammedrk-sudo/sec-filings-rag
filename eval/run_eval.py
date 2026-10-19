import json
import chromadb
from sentence_transformers import SentenceTransformer

K = 5
# a retrieved chunk is a hit if it contains ANY of these strings
EVIDENCE = {
    "q01": ["limited sources of supply", "sole source providers"],
    "q02": ["EU AI Act"],
    "q03": ["threat actors are using and exploiting"],
    "q04": ["Microsoft, Oracle, SAP, Salesforce and Workday"],
    "q05": ["41,525", "41.5 billion"],
    "q06": ["23,769"],
    "q07": ["28.1 billion", "28,101"],
}

model = SentenceTransformer("all-MiniLM-L6-v2")
client = chromadb.PersistentClient(path="data/chroma")
cols = {n: client.get_collection(n) for n in ("fixed", "section")}
qs = [q for q in json.load(open("eval/questions.json", encoding="utf-8")) if q["id"] in EVIDENCE]

tot = {n: {1: 0, 3: 0, K: 0} for n in cols}
for q in qs:
    emb = model.encode([q["question"]]).tolist()
    where = {"$and": [{"company": q["company"]}, {"period": q["period"]}]}
    for name, col in cols.items():
        res = col.query(query_embeddings=emb, n_results=K, where=where)
        rank = next((i + 1 for i, d in enumerate(res["documents"][0])
                     if any(t in d for t in EVIDENCE[q["id"]])), None)
        print(f"{q['id']:<5}{name:<9}{rank or 'miss'}")
        for k in tot[name]:
            if rank and rank <= k:
                tot[name][k] += 1

print()
for name, t in tot.items():
    print(name, {f"hit@{k}": f"{v}/{len(qs)}" for k, v in t.items()})