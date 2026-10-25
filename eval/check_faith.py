import json
import re

d = json.load(open("eval/answers.json", encoding="utf-8"))
for r in d["rows"]:
    if r["refused"] or r["type"] == "unanswerable":
        continue
    print("=" * 80)
    print(r["id"], r["question"])
    print("ANSWER:", r["answer"][:900])
    print("CITED CHUNKS RETRIEVED:", r["cited_chunks"])
    tags = re.findall(r"([A-Z]+ \d{4}-\d\d-\d\d \w+ \d+)", r["answer"])
    outside = [t for t in set(tags) if t not in r["cited_chunks"]]
    print("tags in answer:", len(set(tags)), "| tags NOT among retrieved chunks:", outside)