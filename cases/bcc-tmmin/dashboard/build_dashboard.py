"""Build dashboard/index.html: one self-contained page with every result of the case.

Every number is read from the file that produces it, never retyped:
  model/sd_results.json        system dynamics (written by model/sd_model.py)
  model/run_tests.py stdout    spreadsheet stress test, tornado, sealer simulation
  work/2_diagnosis_calc.py     heat map scores and the cost bridge
  work/4_scoring.py            option scores, weights, random-weight results
  work/6_roadmap.md, 7_kpis.md, 8_qa.md   tables shown as text
Run from the case root:
  node dashboard/check_parity.js && python dashboard/build_dashboard.py
"""
import ast
import contextlib
import io
import json
import re
import runpy
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent


def quiet_run(path):
    with contextlib.redirect_stdout(io.StringIO()):
        return runpy.run_path(str(path))


def py_literal(text):
    return ast.literal_eval(re.sub(r"np\.float64\(([^)]*)\)", r"\1", text))


def stress_test():
    out = subprocess.run([sys.executable, "run_tests.py"], cwd=ROOT / "model", capture_output=True, text=True)
    assert out.returncode == 0, out.stderr[-400:]
    lines = out.stdout.splitlines()
    get = lambda prefix: next(l for l in lines if l.startswith(prefix))
    base = re.search(r"base NPV ([\d.]+) run-rate ([\d.]+)", get("base NPV"))
    sim = []
    for l in lines:
        m = re.match(r"^(\d)\. (.*?) (\{.*\})$", l)
        if m:
            d = py_literal(m.group(3))
            sim.append({"label": m.group(2), "scrap_red": d["scrap_red"], "esc_red": d["esc_red"]})
    strat = []
    for l in lines:
        m = re.match(r"^STRAT ([A-G])\. (.*?) (\{.*\})$", l)
        if m:
            d = py_literal(m.group(3))
            strat.append({"id": m.group(1), "label": m.group(2), **{k: d[k] for k in ("p5", "p50", "p95", "prob_pos", "mean")}})
    return {
        "npv": float(base.group(1)), "runRate": float(base.group(2)), "sim": sim,
        "sens": [{"name": n, "points": pts} for n, pts in py_literal(get("sens ")[5:])],
        "dismiss": py_literal(get("dismiss ")[8:]),
        "strategies": strat,
        "tornado": [{"name": n, "lo": lo, "hi": hi} for n, lo, hi in py_literal(get("tornado ")[8:])],
        "gateStop": float(get("gate stop share").split()[-1]),
    }


def md_tables(path):
    """Map each '##'/'###' heading to the markdown tables under it (rows of cells)."""
    tables, head, cur = {}, None, None
    for line in Path(path).read_text().splitlines():
        if line.startswith("#"):
            head, cur = line.lstrip("# ").strip(), None
            continue
        if line.startswith("|"):
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            if all(re.fullmatch(r":?-{3,}:?", c) for c in cells):
                continue
            cells = [re.sub(r"\*\*|`", "", c) for c in cells]
            if cur is None:
                cur = []
                tables.setdefault(head, []).append(cur)
            cur.append(cells)
        else:
            cur = None
    return tables


def section(tables, startswith):
    key = next(k for k in tables if k.startswith(startswith))
    return tables[key]


def blockquotes(path, startswith):
    text = Path(path).read_text()
    part = text[text.index(startswith):]
    part = part[:part.index("\n## ", 5)] if "\n## " in part[5:] else part
    items = []
    for m in re.finditer(r"\*\*(Q\d+ — .*?)\*\*\n> (.*?)\n", part):
        items.append({"q": m.group(1), "a": m.group(2).strip('"“”')})
    return items


def main():
    sd = json.loads((ROOT / "model" / "sd_results.json").read_text())
    xl = stress_test()
    diag = quiet_run(ROOT / "work" / "2_diagnosis_calc.py")
    score = quiet_run(ROOT / "work" / "4_scoring.py")
    road = md_tables(ROOT / "work" / "6_roadmap.md")
    kpi = md_tables(ROOT / "work" / "7_kpis.md")
    qa = md_tables(ROOT / "work" / "8_qa.md")
    facts = md_tables(ROOT / "data" / "facts.md")

    data = {
        "sd": {
            "params": sd["params"],
            "mc": {k: {kk: v[kk] for kk in ("p_pos", "p5", "p50", "p95", "gate_stop")} for k, v in sd["mc"].items()},
            "tornado": [{"name": n, "lo": lo, "hi": hi} for n, lo, hi in sd["tornado"]],
            "social": sd["social"],
        },
        "xl": xl,
        "ex": {k.split(".")[0].replace("Exhibit ", ""): v[0] for k, v in facts.items() if k.startswith("Exhibit")},
        "diag": {
            "procs": {k: list(v) for k, v in diag["procs"].items()},
            "top3": diag["top3_count"],
            "bridge": {"esc": diag["p_esc"], "scrap": diag["p_scrap"], "nva": diag["p_nva"], "maintHi": diag["p_maint_hi"],
                       "driftLo": diag["drift_lo"], "driftHi": diag["drift_hi"]},
            "shareTmmin": diag["share_t"], "widen": diag["widen"],
            "impl": [diag["impl23"], diag["impl25"]],
        },
        "score": {
            "criteria": [list(c) for c in score["CRITERIA"]],
            "options": {k: list(v) for k, v in score["OPTIONS"].items()},
            "rank1": {n: float(r) for n, r in zip(score["names"], score["rank1"])},
            "pcrit": [list(c) for c in score["PCRIT"]],
            "pilots": {k: list(v) for k, v in score["PILOTS"].items()},
            "pilotRank1": {n: float(r) for n, r in zip(score["pn"], score["r1"])},
        },
        "road": {
            "phases": section(road, "2. Fase")[0], "gate": section(road, "3. Gate")[0],
            "days": section(road, "4. Seratus")[0], "capability": section(road, "5. Rencana")[0],
            "build": section(road, "6. Bangun")[0], "risks": section(road, "7. Risk")[0],
        },
        "kpi": {"outcome": section(kpi, "1. KPI hasil")[0], "driver": section(kpi, "2. KPI pendorong")[0],
                "sustain": section(kpi, "3. KPI keberlanjutan")[0], "fixes": section(kpi, "4. Koreksi")[0]},
        "qa": {"bank": section(qa, "2. Bank")[0],
               "lenses": {k: v[0] for k, v in qa.items() if k.startswith("Lensa")},
               "tally": section(qa, "Aturan tally")[0],
               "spoken": blockquotes(ROOT / "work" / "8_qa.md", "## 3.")},
    }
    html = (HERE / "template.html").read_text()
    for anchor, value in (("/*__SD_MODEL__*/", (HERE / "sd_model.js").read_text()),
                          ("/*__FIN_MODEL__*/", (HERE / "fin_model.js").read_text()),
                          ("/*__DATA__*/", json.dumps(data, separators=(",", ":"), ensure_ascii=False))):
        assert html.count(anchor) == 1, anchor
        html = html.replace(anchor, value)
    (HERE / "index.html").write_text(html)
    print(f"wrote dashboard/index.html ({len(html) // 1024} KB)")


if __name__ == "__main__":
    main()
