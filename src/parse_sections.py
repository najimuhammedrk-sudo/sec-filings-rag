import json
import re
from pathlib import Path
from bs4 import BeautifulSoup

RAW = Path("data/raw")
OUT = Path("data/sections")
WANTED = {
    "1": "Business",
    "1A": "Risk Factors",
    "7": "Management Discussion and Analysis",
    "7A": "Market Risk Disclosures",
}
# Item headings at the start of a line, e.g. "Item 1A." or "ITEM 7"
ITEM_RE = re.compile(r"^item\s+(\d{1,2}[A-C]?)\b", re.IGNORECASE | re.MULTILINE)
MIN_CHARS = {"1": 5000, "1A": 10000, "7": 10000, "7A": 500}


def html_to_text(path):
    soup = BeautifulSoup(path.read_bytes(), "lxml")
    for tag in soup.find_all(["script", "style", "ix:header"]):
        tag.decompose()
    text = soup.get_text("\n")
    text = text.replace("\xa0", " ")
    lines = [re.sub(r"[ \t]+", " ", ln).strip() for ln in text.split("\n")]
    return "\n".join(ln for ln in lines if ln)


def split_sections(text):
    marks = [(m.start(), m.group(1).upper()) for m in ITEM_RE.finditer(text)]
    best = {}
    for i, (start, key) in enumerate(marks):
        if key not in WANTED:
            continue
        end = len(text)
        for nstart, nkey in marks[i + 1:]:
            if nkey != key:
                end = nstart
                break
        # the table of contents also has these headings, so keep the longest span
        if key not in best or (end - start) > (best[key][1] - best[key][0]):
            best[key] = (start, end)
    return {k: text[s:e].strip() for k, (s, e) in best.items()}


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    print(f"{'filing':<24}" + "".join(f"{k:>10}" for k in WANTED))
    for path in sorted(RAW.glob("*_10K.html")):
        ticker, period, _ = path.stem.split("_")
        secs = split_sections(html_to_text(path))
        row = f"{path.stem:<24}"
        for key in WANTED:
            body = secs.get(key, "")
            flag = "*" if len(body) < MIN_CHARS[key] else ""
            row += f"{len(body):>9}{flag or ' '}"
            if body:
                rec = {
                    "company": ticker,
                    "period": period,
                    "form": "10-K",
                    "item": key,
                    "title": WANTED[key],
                    "text": body,
                }
                (OUT / f"{ticker}_{period}_{key}.json").write_text(
                    json.dumps(rec), encoding="utf-8"
                )
        print(row)
    print("* = suspiciously short, inspect by hand")


if __name__ == "__main__":
    main()