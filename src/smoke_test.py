import json
import chromadb
from sentence_transformers import SentenceTransformer

model = SentenceTransformer("all-MiniLM-L6-v2")
client = chromadb.PersistentClient(path="data/chroma")
cols = {n: client.get_collection(n) for n in ("fixed", "section")}
qs = json.load(open("eval/questions.json", encoding="utf-8"))

for q in qs:
    print("=" * 90)
    print(q["id"], q["type"], q["company"], q["period"])
    print(q["question"])
    emb = model.encode([q["question"]]).tolist()
    where = {"$and": [{"company": q["company"]}, {"period": q["period"]}]}
    for name, col in cols.items():
        res = col.query(query_embeddings=emb, n_results=3, where=where)
        print(f"--- {name}")
        for doc, meta, dist in zip(res["documents"][0], res["metadatas"][0], res["distances"][0]):
            hit = q["source_quote"][:60] in doc if q["source_quote"] else False
            print(f"  item {meta['item']} chunk {meta['chunk']} dist {dist:.3f} quote_in_chunk={hit}")
            print("   ", doc[:200].replace("\n", " "))
