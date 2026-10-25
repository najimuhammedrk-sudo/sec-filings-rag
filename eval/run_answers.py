import json
import sys
import time

sys.path.insert(0, "src")
from answer import answer, MODEL

PAUSE = 6  # seconds between calls, for the free-tier rate limit
qs = json.load(open("eval/questions.json", encoding="utf-8"))
rows = []

for q in qs:
    out, metas, dists = answer(q["question"])
    refused = out.strip().upper().startswith("REFUSE")
    if out == "ERROR":
        refused = None
    rows.append({
        "id": q["id"],
        "type": q["type"],
        "question": q["question"],
        "answer": out,
        "refused": refused,
        "best_distance": round(dists[0], 3),
        "cited_chunks": [f"{m['company']} {m['period']} {m['item']} {m['chunk']}" for m in metas],
        "gold_answer": q["gold_answer"],
    })
    print(f"{q['id']:<5}{q['type']:<13}refused={refused}")
    time.sleep(PAUSE)

json.dump({"model": MODEL, "rows": rows}, open("eval/answers.json", "w", encoding="utf-8"), indent=2)

unans = [r for r in rows if r["type"] == "unanswerable"]
ans = [r for r in rows if r["type"] != "unanswerable"]
print(f"\nmodel: {MODEL}")
print(f"unanswerable correctly refused: {sum(r['refused'] is True for r in unans)}/{len(unans)}")
print(f"answerable wrongly refused:     {sum(r['refused'] is True for r in ans)}/{len(ans)}")
print("errors:", sum(r["refused"] is None for r in rows))