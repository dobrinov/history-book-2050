"""Fetch peer-comparison series (BG, RO, HR, RS, SK, PL, EU27) from Eurostat and the World Bank.

Writes data/peers_raw.json. Run: python3 scripts/fetch_peers.py
"""
import json, urllib.request, urllib.parse, itertools, sys, time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
GEOS = ["BG", "RO", "HR", "RS", "SK", "PL", "EU27_2020"]
ES = "https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/"

EUROSTAT = {
    "aic_pps": ("prc_ppp_ind", {"na_item": "VI_PPS_EU27_2020_HAB", "ppp_cat": "A01"}),
    "gdp_pps": ("prc_ppp_ind", {"na_item": "VI_PPS_EU27_2020_HAB", "ppp_cat": "GDP"}),
    "medinc_pps": ("ilc_di03", {"age": "TOTAL", "sex": "T", "statinfo": "MED_EI", "unit": "PPS"}),
    "unemp": ("une_rt_a", {"age": "Y15-74", "unit": "PC_ACT", "sex": "T"}),
    "emp": ("lfsi_emp_a", {"age": "Y20-64", "sex": "T", "indic_em": "EMP_LFS", "unit": "PC_POP"}),
    "hicp": ("prc_hicp_aind", {"coicop": "CP00", "unit": "RCH_A_AVG"}),
    "smd": ("ilc_mddd11", {"age": "TOTAL", "sex": "T", "unit": "PC"}),
    "arope": ("ilc_peps01n", {"age": "TOTAL", "sex": "T", "unit": "PC"}),
    "arope65": ("ilc_peps01n", {"age": "Y_GE65", "sex": "T", "unit": "PC"}),
    "life": ("demo_mlexpec", {"age": "Y_LT1", "sex": "T", "unit": "YR"}),
    "infant": ("demo_minfind", {"unit": "RT", "indic_de": "INFMORRT"}),
    "warm": ("ilc_mdes01", {"hhcomp": "TOTAL", "rskpovth": "TOTAL", "unit": "PC"}),
    "overcrowd": ("ilc_lvho05a", {"age": "TOTAL", "sex": "T", "rskpovth": "TOTAL", "unit": "PC"}),
    "debt": ("gov_10dd_edpt1", {"na_item": "GD", "sector": "S13", "unit": "PC_GDP"}),
    "deficit": ("gov_10dd_edpt1", {"na_item": "B9", "sector": "S13", "unit": "PC_GDP"}),
    "prod": ("nama_10_lp_ulc", {"na_item": "NLPR_PER", "unit": "PC_EU27_2020_MPPS_CP"}),
    "energy_dep": ("nrg_ind_id", {"siec": "TOTAL", "unit": "PC"}),
    "gini": ("ilc_di12", {}),
    "early": ("edat_lfse_14", {"sex": "T", "wstatus": "POP", "unit": "PC"}),
    "tertiary": ("edat_lfse_03", {"sex": "T", "age": "Y30-34", "isced11": "ED5-8", "unit": "PC"}),
    "excess_mort": ("demo_mexrt", {"unit": "PC"}),
}
REGIONS = {"gdp_reg": ("nama_10r_2gdp", {"unit": "PPS_EU27_2020_HAB"}, ["BG31", "BG32", "BG33", "BG34", "BG41", "BG42", "EU27_2020"])}

WB = {
    "wb_gdp_pc_ppp": "NY.GDP.PCAP.PP.KD",
    "wb_pop": "SP.POP.TOTL",
    "wb_life": "SP.DYN.LE00.IN",
    "wb_infl": "FP.CPI.TOTL.ZG",
    "wb_unemp": "SL.UEM.TOTL.ZS",
    "wb_fdi": "BX.KLT.DINV.WD.GD.ZS",
    "wb_fert": "SP.DYN.TFRT.IN",
    "wb_rl": "GOV_WGI_RL.EST",
    "wb_cc": "GOV_WGI_CC.EST",
    "wb_ge": "GOV_WGI_GE.EST",
    "wb_va": "GOV_WGI_VA.EST",
    "wb_growth": "NY.GDP.MKTP.KD.ZG",
    "wb_extdebt": "DT.DOD.DECT.CD",
    "wb_ca": "BN.CAB.XOKA.GD.ZS",
}
WB_ISO = {"BG": "BGR", "RO": "ROU", "HR": "HRV", "RS": "SRB", "SK": "SVK", "PL": "POL"}


def get(url, tries=3):
    for i in range(tries):
        try:
            with urllib.request.urlopen(url, timeout=60) as r:
                return json.load(r)
        except Exception as e:
            if i == tries - 1:
                raise
            time.sleep(2)


def eurostat(code, params, geos):
    q = [("format", "JSON"), ("lang", "en")] + [(k, v) for k, v in params.items()] + [("geo", g) for g in geos]
    j = get(ES + code + "?" + urllib.parse.urlencode(q))
    ids, size = j["id"], j["size"]
    cats = []
    for d in ids:
        idx = j["dimension"][d]["category"]["index"]
        a = [None] * len(idx)
        for c, i in idx.items():
            a[i] = c
        cats.append(a)
    out = {}
    for flat, v in j["value"].items():
        n = int(flat)
        coord = [None] * len(ids)
        for i in range(len(ids) - 1, -1, -1):
            coord[i] = cats[i][n % size[i]]
            n //= size[i]
        geo = coord[ids.index("geo")]
        t = coord[ids.index("time")]
        extra = [coord[i] for i in range(len(ids)) if size[i] > 1 and ids[i] not in ("geo", "time")]
        key = geo if not extra else geo + "|" + "|".join(extra)
        out.setdefault(key, {})[t] = v
    return {"updated": j.get("updated"), "series": out}


def worldbank(ind):
    iso = ";".join(WB_ISO.values())
    j = get(f"https://api.worldbank.org/v2/country/{iso}/indicator/{ind}?format=json{"&source=3" if ind.startswith("GOV_WGI") else ""}&per_page=2000&date=1984:2025")
    out = {}
    inv = {v: k for k, v in WB_ISO.items()}
    for r in j[1] or []:
        if r["value"] is None:
            continue
        out.setdefault(inv[r["countryiso3code"]], {})[r["date"]] = r["value"]
    return {"updated": j[0].get("lastupdated"), "series": out}


def gas_share():
    """Share of Russia in Bulgaria's natural-gas imports, % (Eurostat nrg_ti_gas)."""
    r = eurostat("nrg_ti_gas", {"siec": "G3000", "unit": "TJ_GCV", "partner": "RU"}, ["BG"])["series"]["BG"]
    t = eurostat("nrg_ti_gas", {"siec": "G3000", "unit": "TJ_GCV", "partner": "TOTAL"}, ["BG"])["series"]["BG"]
    return {"source": "Eurostat nrg_ti_gas", "series": {"BG": {y: round(100 * r[y] / t[y], 1) for y in t if y in r and t[y]}}}


def main():
    res = {}
    try:
        res["gas_ru"] = gas_share()
        print("ok gas_ru")
    except Exception as e:
        print("ERR gas_ru", e, file=sys.stderr)
    for k, (code, p) in EUROSTAT.items():
        try:
            try:
                r = eurostat(code, p, GEOS)
            except Exception:
                r = eurostat(code, p, [g for g in GEOS if g != "RS"])
            res[k] = {"source": f"Eurostat {code}", **r}
            print("ok", k, list(res[k]["series"].keys())[:8])
        except Exception as e:
            print("ERR", k, e, file=sys.stderr)
    for k, (code, p, geos) in REGIONS.items():
        try:
            res[k] = {"source": f"Eurostat {code}", **eurostat(code, p, geos)}
            print("ok", k)
        except Exception as e:
            print("ERR", k, e, file=sys.stderr)
    for k, ind in WB.items():
        try:
            res[k] = {"source": f"World Bank WDI {ind}", **worldbank(ind)}
            print("ok", k, list(res[k]["series"].keys()))
        except Exception as e:
            print("ERR", k, e, file=sys.stderr)
    (ROOT / "data/peers_raw.json").write_text(json.dumps(res, ensure_ascii=False))


if __name__ == "__main__":
    main()
