"""Fetch World Bank series for the "Какво ако?" page.

Bulgaria (reality) and the proxy countries for each scenario: Estonia, Latvia, Lithuania (Baltic path),
Poland, Slovakia (Central European path), Romania (Romanian path), Serbia, North Macedonia
(outside the EU), Belarus, Armenia (Eurasian path).
Writes data/whatif_raw.json. Run: python3 scripts/fetch_whatif.py
"""
import json, sys, time, urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ISO = {"BG": "BGR", "RO": "ROU", "RS": "SRB", "MK": "MKD", "BY": "BLR", "AM": "ARM",
       "EE": "EST", "LV": "LVA", "LT": "LTU", "PL": "POL", "SK": "SVK", "EU": "EUU"}
IND = {
    "gdp_ppp": "NY.GDP.PCAP.PP.KD",
    "pop": "SP.POP.TOTL",
    "life": "SP.DYN.LE00.IN",
    "infl": "FP.CPI.TOTL.ZG",
    "fdi": "BX.KLT.DINV.WD.GD.ZS",
    "unemp": "SL.UEM.TOTL.ZS",
    "remit": "BX.TRF.PWKR.DT.GD.ZS",
    "growth": "NY.GDP.MKTP.KD.ZG",
    "infant": "SP.DYN.IMRT.IN",
    "rl": "GOV_WGI_RL.EST",
    "va": "GOV_WGI_VA.EST",
    "cc": "GOV_WGI_CC.EST",
    "ps": "GOV_WGI_PV.EST",
}


def get(url):
    for i in range(3):
        try:
            with urllib.request.urlopen(url, timeout=60) as r:
                return json.load(r)
        except Exception:
            if i == 2:
                raise
            time.sleep(2)


def main():
    inv = {v: k for k, v in ISO.items()}
    out = {}
    for k, ind in IND.items():
        src = "&source=3" if ind.startswith("GOV_WGI") else ""
        j = get(f"https://api.worldbank.org/v2/country/{';'.join(ISO.values())}/indicator/{ind}?format=json&per_page=5000&date=1989:2025{src}")
        s = {}
        for r in j[1] or []:
            if r["value"] is not None:
                s.setdefault(inv[r["countryiso3code"]], {})[r["date"]] = r["value"]
        out[k] = {"source": f"World Bank {ind}", "series": s}
        print("ok", k, {c: len(v) for c, v in s.items()})
    (ROOT / "data/whatif_raw.json").write_text(json.dumps(out))


if __name__ == "__main__":
    main()
