# EDGAR fair access: User-Agent with name and email required.
# Rate limit per SEC docs: <fill in from sec.gov>
import requests

HEADERS = {"User-Agent": "Naji Muhammed your_email@example.com"}
TICKERS = ["MSFT", "ORCL", "CRM", "ADBE", "NOW", "INTU", "WDAY", "PANW"]

r = requests.get("https://www.sec.gov/files/company_tickers.json", headers=HEADERS)
r.raise_for_status()
data = r.json()

lookup = {v["ticker"]: str(v["cik_str"]).zfill(10) for v in data.values()}
for t in TICKERS:
    print(t, lookup.get(t, "NOT FOUND"))