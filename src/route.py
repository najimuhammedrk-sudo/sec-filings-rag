import re
from pathlib import Path

ALIASES = {
    "MSFT": r"\bmicrosoft\b|\bmsft\b",
    "ORCL": r"\boracle\b|\borcl\b",
    "CRM": r"\bsalesforce\b|\bcrm\b",
    "ADBE": r"\badobe\b|\badbe\b",
    "NOW": r"\bservicenow\b|\bservice now\b",
    "INTU": r"\bintuit\b|\bintu\b",
    "WDAY": r"\bworkday\b|\bwday\b",
    "PANW": r"\bpalo alto\b|\bpanw\b",
}

# periods that actually exist, read from the section filenames
PERIODS = {}
for p in Path("data/sections").glob("*.json"):
    company, period, _ = p.stem.split("_")
    PERIODS.setdefault(company, set()).add(period)


def route(question):
    """Return (ticker or None, sorted list of matching periods)."""
    low = question.lower()
    best = None
    for tick, pat in ALIASES.items():
        m = re.search(pat, low)
        if m and (best is None or m.start() < best[1]):
            best = (tick, m.start())
    if best is None:
        return None, []
    tick = best[0]
    years = set(re.findall(r"\b(20\d\d)\b", question))
    periods = sorted(p for p in PERIODS.get(tick, []) if p[:4] in years)
    if not periods:
        periods = [max(PERIODS.get(tick, []))]
    return tick, periods

def build_where(tick, periods):
    if not tick:
        return None
    clauses = [{"company": tick}]
    if len(periods) == 1:
        clauses.append({"period": periods[0]})
    elif len(periods) > 1:
        clauses.append({"period": {"$in": periods}})
    return clauses[0] if len(clauses) == 1 else {"$and": clauses}