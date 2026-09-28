"""Clean data/peers_raw.json plus hand-collected series into data/peers.json for the page."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
raw = json.loads((ROOT / "data/peers_raw.json").read_text())
C = ["BG", "RO", "HR", "RS", "SK", "PL", "EU"]


def series(key, geo_filter=None, rnd=1, first=1984, last=2026):
    s = raw[key]["series"]
    out = {}
    for k, v in s.items():
        parts = k.split("|")
        geo = "EU" if parts[0] == "EU27_2020" else parts[0]
        if geo not in C:
            continue
        if geo_filter and not geo_filter(parts):
            continue
        pts = sorted((int(y), round(float(val), rnd)) for y, val in v.items()
                     if len(y) == 4 and first <= int(y) <= last and val is not None)
        if pts:
            out[geo] = [list(p) for p in pts]
    return out


def index(s, base):
    out = {}
    for g, pts in s.items():
        b = dict(pts).get(base)
        if b:
            out[g] = [[y, round(v / b * 100, 1)] for y, v in pts if y >= base]
    return out


P = {}
P["aic"] = series("aic_pps", rnd=0)
P["gdp_pps"] = series("gdp_pps", rnd=0)
P["gdp_idx"] = index(series("wb_gdp_pc_ppp", rnd=1), 1990)
P["pop_idx"] = index(series("wb_pop", rnd=0), 1989)
P["life"] = series("wb_life", rnd=1)
P["unemp"] = series("wb_unemp", rnd=1)
P["growth"] = series("wb_growth", rnd=1)
P["infl"] = series("wb_infl", rnd=1)
P["fert"] = series("wb_fert", rnd=2)
P["fdi"] = series("wb_fdi", rnd=1)
P["extdebt"] = {"BG": [[y, round(v / 1e9, 1)] for y, v in series("wb_extdebt", rnd=0)["BG"] if y <= 2000]}
P["ca"] = series("wb_ca", rnd=1)
for k in ("rl", "cc", "va", "ge"):
    P[k] = series("wb_" + k, rnd=2)
P["prod"] = series("prod", rnd=0)
P["debt"] = series("debt", rnd=1)
P["deficit"] = series("deficit", rnd=1)
P["arope"] = series("arope", rnd=1)
P["arope65"] = series("arope65", rnd=1)
P["warm"] = series("warm", rnd=1)
P["overcrowd"] = series("overcrowd", rnd=1)
P["medinc"] = series("medinc_pps", rnd=0)
P["emp"] = series("emp", rnd=1)
P["gini"] = series("gini", geo_filter=lambda p: len(p) == 1 or p[1] == "TOTAL", rnd=1)
P["early"] = series("early", rnd=1)
P["tertiary"] = series("tertiary", rnd=1)
P["energy_dep"] = series("energy_dep", rnd=1)
P["infant"] = series("infant", rnd=1)

# Excess mortality: annual mean of monthly % over the 2016-19 baseline.
ex = {}
for k, v in raw["excess_mort"]["series"].items():
    geo = "EU" if k == "EU27_2020" else k
    yrs = {}
    for ym, val in v.items():
        if val is None:
            continue
        yrs.setdefault(int(ym[:4]), []).append(val)
    ex[geo] = [[y, round(sum(a) / len(a), 1)] for y, a in sorted(yrs.items()) if len(a) == 12]
P["excess"] = ex

# Regional GDP per head in PPS, as % of EU27.
reg = raw["gdp_reg"]["series"]
eu = reg["EU27_2020"]
P["regions"] = {k: [[int(y), round(v / eu[y] * 100)] for y, v in sorted(reg[k].items()) if y in eu]
                for k in reg if k != "EU27_2020"}

P["gas_ru"] = {"BG": [[int(y), v] for y, v in sorted(raw["gas_ru"]["series"]["BG"].items())]}

# Hand-collected (see sources on the page).
# RSF World Press Freedom Index rank, Bulgaria (rsf.org/en/index, retrieved Sept 2026). No 2011 edition.
P["rsf"] = {"BG": [[2002, 38], [2003, 34], [2004, 36], [2005, 48], [2006, 36], [2007, 51], [2008, 59], [2009, 68],
                   [2010, 71], [2012, 81], [2013, 87], [2014, 100], [2015, 106], [2016, 113], [2017, 109], [2018, 111],
                   [2019, 111], [2020, 111], [2021, 112], [2022, 91], [2023, 71], [2024, 59], [2025, 70], [2026, 71]],
            "RO": [[2019, 47], [2020, 48], [2021, 48], [2022, 56], [2023, 53], [2024, 49], [2025, 55], [2026, 49]],
            "HR": [[2019, 64], [2020, 59], [2021, 56], [2022, 48], [2023, 42], [2024, 48], [2025, 60], [2026, 53]],
            "RS": [[2019, 90], [2020, 93], [2021, 93], [2022, 79], [2023, 91], [2024, 98], [2025, 96], [2026, 104]],
            "SK": [[2019, 35], [2020, 33], [2021, 35], [2022, 27], [2023, 17], [2024, 29], [2025, 38], [2026, 37]],
            "PL": [[2019, 59], [2020, 62], [2021, 64], [2022, 66], [2023, 57], [2024, 47], [2025, 31], [2026, 27]]}
# Transparency International CPI, 0-100 scale (comparable from 2012). Via Wikipedia list, retrieved Sept 2026.
CPI = {
    "BG": [41, 41, 43, 41, 41, 43, 42, 43, 44, 42, 43, 45, 43, 40],
    "RO": [44, 43, 43, 46, 48, 48, 47, 44, 44, 45, 46, 46, 46, 45],
    "HR": [46, 48, 48, 51, 49, 49, 48, 47, 47, 47, 50, 50, 47, 47],
    "RS": [39, 42, 41, 40, 42, 41, 39, 39, 38, 38, 36, 36, 35, 33],
    "SK": [46, 47, 50, 51, 51, 50, 50, 50, 49, 52, 53, 54, 49, 48],
    "PL": [58, 60, 61, 63, 62, 60, 60, 58, 56, 56, 55, 54, 53, 52],
}
P["cpi"] = {g: [[2012 + i, v] for i, v in enumerate(vals)] for g, vals in CPI.items()}
# Turnout in parliamentary elections, % (Wikipedia infoboxes citing CIK).
P["turnout"] = [["1990", 1990.45, 90.8], ["1991", 1991.8, 83.9], ["1994", 1994.97, 75.2], ["1997", 1997.3, 58.9],
                ["2001", 2001.47, 66.6], ["2005", 2005.48, 55.8], ["2009", 2009.51, 60.6], ["2013", 2013.37, 52.5],
                ["2014", 2014.76, 51.1], ["2017", 2017.24, 53.9], ["апр 2021", 2021.26, 49.1],
                ["юли 2021", 2021.53, 41.6], ["ное 2021", 2021.87, 40.0], ["2022", 2022.75, 39.3],
                ["2023", 2023.25, 40.5], ["юни 2024", 2024.44, 34.4], ["окт 2024", 2024.82, 38.8],
                ["2026", 2026.3, 50.7]]

(ROOT / "data/peers.json").write_text(json.dumps(P, ensure_ascii=False, separators=(",", ":")))
print("wrote data/peers.json", len(json.dumps(P)) // 1024, "KB")
for k in ("aic", "gdp_idx", "pop_idx", "excess", "regions"):
    print(k, {g: (v[0], v[-1]) for g, v in P[k].items()})
