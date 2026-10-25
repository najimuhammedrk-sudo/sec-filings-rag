import os
import sys
import time

sys.path.insert(0, "src")
import chromadb
from dotenv import load_dotenv
from google import genai
from sentence_transformers import SentenceTransformer

from route import route, build_where

load_dotenv()
MODEL = "gemini-flash-lite-latest"  # change to the model name shown in AI Studio
COLLECTION = "fixed"
K = 5

embedder = SentenceTransformer("all-MiniLM-L6-v2")
col = chromadb.PersistentClient(path="data/chroma").get_collection(COLLECTION)
client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

PROMPT = """You answer questions about SEC 10-K filings using ONLY the passages below.
Rules:
- Use only facts stated in the passages. Do not use outside knowledge.
- Cite every claim as [COMPANY period item chunk], for example [CRM 2026-01-31 1A 14].
- If the passages do not contain the answer, reply with exactly: REFUSE
- If the passages only partly answer, answer the part they support and say what is missing.

PASSAGES:
{passages}

QUESTION: {question}

ANSWER:"""

import re

STOP = {"what", "did", "the", "and", "for", "how", "was", "were", "its", "their",
        "report", "versus", "from", "with", "that", "this", "between", "does",
        "say", "cite", "about", "which", "into", "than", "has", "have"}


def keyword_hits(question, tick, periods, n=4):
    terms = [w for w in re.findall(r"[a-z0-9%$]+", question.lower())
             if len(w) > 3 and w not in STOP]
    if not tick or not terms:
        return []
    where = build_where(tick, periods)
    r = col.get(where=where, include=["documents", "metadatas"])
    scored = []
    for d, m in zip(r["documents"], r["metadatas"]):
        low = d.lower()
        score = sum(1 for t in terms if t in low)
        figures = len(re.findall(r"\$ ?\d[\d,]*", d))
        if any(t in terms for t in ("revenue", "growth", "total", "rate")):
            score += min(figures, 6)
        scored.append((score, d, m))
    scored.sort(key=lambda s: -s[0])
    return [(d, m, 0.5) for s, d, m in scored[:n] if s >= 6]

def retrieve(question):
    tick, periods = route(question)
    emb = embedder.encode([question]).tolist()

    def run(where, n):
        kw = dict(query_embeddings=emb, n_results=n,
                  include=["documents", "metadatas", "distances"])
        if where:
            kw["where"] = where
        r = col.query(**kw)
        return list(zip(r["documents"][0], r["metadatas"][0], r["distances"][0]))

    if tick and len(periods) > 1:
        hits = []
        for p in periods:
            hits += run({"$and": [{"company": tick}, {"period": p}]}, 3)
    else:
        hits = run(build_where(tick, periods), K)
    seen = {(m["period"], m["item"], m["chunk"]) for _, m, _ in hits}
    for d, m, dist in keyword_hits(question, tick, periods):
        if (m["period"], m["item"], m["chunk"]) not in seen:
            hits.append((d, m, dist))
    hits.sort(key=lambda h: h[2])
    docs, metas, dists = zip(*hits)
    return list(docs), list(metas), list(dists)

def call_model(prompt):
    # the only provider-specific function: swap this to change models
    for attempt in range(4):
        try:
            resp = client.models.generate_content(model=MODEL, contents=prompt)
            return (resp.text or "").strip()
        except Exception as e:
            print("model call failed, retrying:", str(e)[:120])
            time.sleep(15 * (attempt + 1))
    return "ERROR"


def answer(question):
    docs, metas, dists = retrieve(question)
    passages = "\n\n".join(
        f"[{m['company']} {m['period']} {m['item']} {m['chunk']}] {d}"
        for d, m in zip(docs, metas))
    out = call_model(PROMPT.format(passages=passages, question=question))
    return out, metas, dists


if __name__ == "__main__":
    q = " ".join(sys.argv[1:])
    out, metas, dists = answer(q)
    print(out)
    print("\nbest distance:", round(dists[0], 3))