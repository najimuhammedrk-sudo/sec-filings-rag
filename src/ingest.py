# EDGAR fair access: User-Agent with name and email required.
# Rate limit per SEC docs: <keep your note from sec.gov>
import time
from pathlib import Path
import requests

HEADERS = {"User-Agent": "najimuhammedrk@gmail.com"}
TICKERS = ["MSFT", "ORCL", "CRM", "ADBE", "NOW", "INTU", "WDAY", "PANW"]
RAW = Path("data/raw")
YEARS = 3
DELAY = 0.2  # seconds between requests, stays well under the SEC limit


def get(url):
    time.sleep(DELAY)
    r = requests.get(url, headers=HEADERS)
    r.raise_for_status()
    return r


def cik_lookup():
    data = get("https://www.sec.gov/files/company_tickers.json").json()
    return {v["ticker"]: v["cik_str"] for v in data.values()}


def tenk_list(cik):
    url = f"https://data.sec.gov/submissions/CIK{str(cik).zfill(10)}.json"
    recent = get(url).json()["filings"]["recent"]
    rows = []
    for i, form in enumerate(recent["form"]):
        if form == "10-K":
            rows.append({
                "accession": recent["accessionNumber"][i],
                "doc": recent["primaryDocument"][i],
                "filed": recent["filingDate"][i],
                "period": recent["reportDate"][i],
            })
    rows.sort(key=lambda r: r["filed"], reverse=True)
    return rows[:YEARS]


def main():
    RAW.mkdir(parents=True, exist_ok=True)
    ciks = cik_lookup()
    for t in TICKERS:
        cik = ciks[t]
        for f in tenk_list(cik):
            acc = f["accession"].replace("-", "")
            url = f"https://www.sec.gov/Archives/edgar/data/{cik}/{acc}/{f['doc']}"
            out = RAW / f"{t}_{f['period']}_10K.html"
            if out.exists():
                print("skip", out.name)
                continue
            out.write_bytes(get(url).content)
            print("saved", out.name, f"{out.stat().st_size // 1024} KB")


if __name__ == "__main__":
    main()