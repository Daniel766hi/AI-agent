"""Number tie-out: every headline number in the deliverables must match a model.

Run from the case root:  python work/8_tieout.py
Re-runs the financial stress test (model/run_tests.py), reads the system
dynamics results (model/sd_results.json, written by model/sd_model.py), and
asserts each headline figure appears, formatted the Indonesian way, in the
documents that quote it. Exits non-zero on any miss, so it is safe to gate on.
"""
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DOCS = {
    "proposal": ROOT / "outputs" / "proposal_draft.md",
    "storyline": ROOT / "work" / "8_storyline.md",
    "kpis": ROOT / "work" / "7_kpis.md",
    "tests": ROOT / "work" / "5_tests.md",
    "qa": ROOT / "work" / "8_qa.md",
}


def idn(x, d=1):
    """12.3 -> '12,3'; thousands with a dot: 1765 -> '1.765'."""
    s = f"{abs(x):,.{d}f}".replace(",", "_").replace(".", ",").replace("_", ".")
    return ("−" if x < 0 else "") + s


def pct(x):
    return f"{round(x * 100):.0f}%"


def spreadsheet_numbers():
    out = subprocess.run([sys.executable, "run_tests.py"], cwd=ROOT / "model", capture_output=True, text=True)
    assert out.returncode == 0, out.stderr[-500:]
    text = out.stdout

    def strat(letter):
        m = re.search(rf"STRAT {letter}\..*?'p5': np\.float64\(([-\d.]+)\).*?'prob_pos': np\.float64\(([\d.]+)\)", text)
        return float(m.group(1)), float(m.group(2))
    m = re.search(r"base NPV ([\d.]+) run-rate ([\d.]+)", text)
    return dict(npv=float(m.group(1)), run_rate=float(m.group(2)), A=strat("A"), C=strat("C"), D=strat("D"), F=strat("F"))


def main():
    sd = json.loads((ROOT / "model" / "sd_results.json").read_text())
    xl = spreadsheet_numbers()
    s, e, mc = sd["summary"], sd["econ"], sd["mc"]
    env = {r["year"]: r for r in sd["env"]}
    checks = [  # (label, expected text, documents that must contain it)
        ("XL NPV base", idn(xl["npv"]), ["proposal", "tests"]),
        ("NPV range, both models", f"{xl['npv']:.0f}–{e['clk_v2']['npv']:.0f}", ["proposal", "storyline"]),
        ("P(NPV>0) range, both models",
         f"{pct(xl['D'][1])[:-1]}–{pct(mc['CLK v2, pilot-light + gate']['p_pos'])}", ["proposal", "storyline"]),
        ("Index range, both models", f"{106 * (1 - xl['run_rate'] / 560):.0f}–{s['clk_v2']['real']:.0f}", ["proposal", "storyline"]),
        ("XL run-rate", idn(xl["run_rate"]), ["proposal", "tests"]),
        ("XL P(NPV>0) pilot-light + gate", pct(xl["D"][1]), ["proposal", "tests"]),
        ("XL P5 pilot-light + gate", idn(xl["D"][0]), ["tests"]),
        ("XL P(NPV>0) one year late", pct(xl["F"][1]), ["proposal", "tests", "qa"]),
        ("XL P(NPV>0) front-loaded", pct(xl["A"][1]), ["proposal", "tests"]),
        ("XL P(NPV>0) pilot-light no gate", pct(xl["C"][1]), ["proposal", "tests"]),
        ("SD index 2030, constant 2025 prices", idn(s["clk_v2"]["real"]), ["proposal", "storyline", "kpis", "tests"]),
        ("SD do-nothing index 2030", idn(s["do_nothing"]["real"]), ["proposal", "storyline", "kpis", "tests"]),
        ("SD tech-only index 2030", idn(s["tech_only"]["real"]), ["proposal", "tests"]),
        ("SD scrap 2030", f"{s['clk_v2']['scrap']:.0f}", ["proposal", "kpis", "tests"]),
        ("SD variant months 2030", idn(s["clk_v2"]["months"]), ["proposal", "kpis", "tests", "qa"]),
        ("SD digital L3+ 2030", idn(s["clk_v2"]["S"]), ["proposal", "kpis", "tests"]),
        ("SD know-how 2030", pct(s["clk_v2"]["K"]), ["proposal", "storyline", "kpis", "tests"]),
        ("SD improvement time 2030", pct(s["clk_v2"]["improve"]), ["proposal", "storyline", "kpis", "tests"]),
        ("SD NPV vs do-nothing", idn(e["clk_v2"]["npv"]), ["proposal", "tests"]),
        ("SD NPV vs frozen 2025", idn(e["clk_v2"]["npv_frozen"]), ["proposal", "tests", "qa"]),
        ("SD NPV 2026-35 vs frozen", idn(e["clk_v2"]["npv35_frozen"]), ["proposal", "tests", "qa"]),
        ("SD P(NPV>0) plan", pct(mc["CLK v2, pilot-light + gate"]["p_pos"]), ["proposal", "tests"]),
        ("SD P(NPV>0) late", pct(mc["CLK v2, 1 year late + gate"]["p_pos"]), ["proposal", "tests", "qa"]),
        ("SD P(NPV>0) failure, pilot-light", pct(mc["FAILURE (adoption 20-60%): pilot-light + gate"]["p_pos"]),
         ["proposal", "tests", "qa"]),
        ("SD P(NPV>0) failure, front-loaded", pct(mc["FAILURE (adoption 20-60%): front-loaded + gate"]["p_pos"]),
         ["proposal", "tests", "qa"]),
        ("SD CO2 avoided 2030", idn(env[2030]["tco2"], 0), ["proposal", "storyline", "kpis", "tests", "qa"]),
        ("SD MWh saved 2030", idn(env[2030]["mwh"], 0), ["proposal", "kpis", "tests"]),
        ("SD durability, kept", idn(s["clk_v2"]["real2035"]), ["proposal", "tests", "qa"]),
        ("SD durability, stopped", idn(s["clk_v2_relapse"]["real2035"]), ["proposal", "tests", "qa"]),
    ]
    texts = {k: p.read_text() for k, p in DOCS.items()}
    deck = ROOT / "outputs" / "deck_closed_loop_kaizen.pptx"
    md = subprocess.run(["markitdown", str(deck)], capture_output=True, text=True)
    assert md.returncode == 0, "markitdown is needed to read the deck: pip install 'markitdown[pptx]'"
    texts["deck"] = md.stdout
    DOCS["deck"] = deck
    deck_checks = ("NPV range, both models", "P(NPV>0) range, both models", "Index range, both models",
                   "XL P(NPV>0) pilot-light + gate", "XL P(NPV>0) one year late", "XL P(NPV>0) front-loaded",
                   "XL P(NPV>0) pilot-light no gate", "SD index 2030, constant 2025 prices", "SD do-nothing index 2030",
                   "SD NPV vs do-nothing", "SD NPV vs frozen 2025", "SD NPV 2026-35 vs frozen", "SD CO2 avoided 2030",
                   "SD durability, kept", "SD durability, stopped", "SD digital L3+ 2030", "SD know-how 2030")
    checks = [(l, w, d + (["deck"] if l in deck_checks else [])) for l, w, d in checks]
    misses = []
    for label, want, where in checks:
        forms = {want, want.replace("−", "−Rp", 1)} if want.startswith("−") else {want}
        for doc in where:
            if not any(f in texts[doc] for f in forms):
                misses.append(f"{label}: '{want}' not in {DOCS[doc].relative_to(ROOT)}")
    for label, want, where in checks:
        print(f"  {'ok  ' if not any(m.startswith(label + ':') for m in misses) else 'MISS'}  {label:<40} {want}")
    if misses:
        print("\n" + "\n".join(misses))
        return 1
    print(f"\n{len(checks)} headline numbers tie out to the models")
    return 0


if __name__ == "__main__":
    sys.exit(main())
