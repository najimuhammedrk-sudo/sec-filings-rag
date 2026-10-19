import json
import re
import sys

key, kw = sys.argv[1], sys.argv[2]
with open(f"data/sections/{key}.json", encoding="utf-8") as f:
    text = json.load(f)["text"]
hits = list(re.finditer(kw, text, re.IGNORECASE))
print(f"{len(hits)} matches, showing up to 5\n")
for m in hits[:5]:
    s, e = max(0, m.start() - 200), min(len(text), m.end() + 400)
    print("...", text[s:e].replace("\n", " "), "...\n")