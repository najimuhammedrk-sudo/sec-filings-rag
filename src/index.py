import json
import re
from pathlib import Path

import chromadb
from sentence_transformers import SentenceTransformer

SECTIONS = Path("data/sections")
DB_PATH = "data/chroma"
MODEL_NAME = "all-MiniLM-L6-v2"
FIXED_WORDS = 150
FIXED_OVERLAP = 30
PARA_MIN_WORDS = 60
PARA_MAX_WORDS = 150




def clean(text):
    lines = [ln.strip() for ln in text.split("\n") if ln.strip()]
    keep = []
    for i, s in enumerate(lines):
        low = s.lower()
        if low in ("table of contents", "part i", "part ii", "part iii"):
            continue
        if re.fullmatch(r"\d{1,3}", s):
            nxt = lines[i + 1].lower() if i + 1 < len(lines) else ""
            if nxt in ("table of contents",) or nxt.startswith("part "):
                continue
        keep.append(s)
    return "\n".join(keep)

def fixed_chunks(text):
    words = text.split()
    step = FIXED_WORDS - FIXED_OVERLAP
    return [" ".join(words[i:i + FIXED_WORDS])
            for i in range(0, max(len(words) - FIXED_OVERLAP, 1), step)]


def para_chunks(text):
    # table cells sit one per line, so merge short lines into running text
    lines = text.split("\n")
    chunks, buf = [], []
    for ln in lines:
        buf.append(ln)
        n = sum(len(b.split()) for b in buf)
        if n >= PARA_MAX_WORDS or (n >= PARA_MIN_WORDS and ln.endswith(".")):
            chunks.append(" ".join(buf))
            buf = []
    if buf:
        tail = " ".join(buf)
        if chunks and len(tail.split()) < PARA_MIN_WORDS:
            chunks[-1] += " " + tail
        else:
            chunks.append(tail)
    return chunks


def main():
    model = SentenceTransformer(MODEL_NAME)
    client = chromadb.PersistentClient(path=DB_PATH)
    for name in ("fixed", "section"):
        try:
            client.delete_collection(name)
        except Exception:
            pass
    cols = {n: client.create_collection(n, metadata={"hnsw:space": "cosine"})
            for n in ("fixed", "section")}

    for path in sorted(SECTIONS.glob("*.json")):
        rec = json.loads(path.read_text(encoding="utf-8"))
        text = clean(rec["text"])
        for kind, fn in (("fixed", fixed_chunks), ("section", para_chunks)):
            chunks = fn(text)
            if not chunks:
                continue
            ids = [f"{rec['company']}_{rec['period']}_{rec['item']}_{kind}_{i}"
                   for i in range(len(chunks))]
            metas = [{"company": rec["company"], "period": rec["period"],
                      "item": rec["item"], "form": rec["form"], "chunk": i}
                     for i in range(len(chunks))]
            embs = model.encode(chunks, batch_size=64).tolist()
            cols[kind].add(ids=ids, documents=chunks, embeddings=embs, metadatas=metas)
        print("indexed", path.stem)

    for n, c in cols.items():
        print(n, c.count(), "chunks")


if __name__ == "__main__":
    main()