"""Clean data/whatif_raw.json into data/whatif.json for the "Какво ако?" page."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
raw = json.loads((ROOT / "data/whatif_raw.json").read_text())
RND = {"gdp_ppp": 0, "pop": 0, "life": 1, "infl": 1, "unemp": 1, "rl": 2, "va": 2, "cc": 2, "fdi": 1, "remit": 1}

W = {}
for k, r in RND.items():
    W[k] = {c: [[int(y), round(v, r) if r else round(v)] for y, v in sorted(s.items(), key=lambda p: int(p[0]))]
            for c, s in raw[k]["series"].items()}
# RSF World Press Freedom Index 2026, rank (rsf.org, via Wikipedia, retrieved Sept 2026).
W["rsf2026"] = {"BG": 71, "EE": 3, "LT": 15, "LV": 17, "PL": 27, "SK": 37, "RO": 49, "RS": 104, "MK": 45, "BY": 165, "AM": 50}
(ROOT / "data/whatif.json").write_text(json.dumps(W, separators=(",", ":")))
print("wrote data/whatif.json", len(json.dumps(W)) // 1024, "KB")
