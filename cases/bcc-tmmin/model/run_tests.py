"""Tests the case ideas with numbers.
1) Closed-loop quality simulation (sealer drift -> inspection -> feedback), episode-based Monte Carlo.
2) Monte Carlo of the financial model (mirrors the Model tab formulas).
3) One-at-a-time tornado sensitivity.
Results are appended to TMMIN_Case_Model.xlsx as a 'Simulation' tab.
"""
import numpy as np
from openpyxl import load_workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.chart import BarChart, Reference

rng = np.random.default_rng(2026)

# ------------------------------------------------------------------ 1. QUALITY SIM
UNITS = 175_000            # Exhibit 9 (~175,000 units/yr)
QP = dict(                 # illustrative process assumptions (labelled in sheet)
    p_normal=0.002,        # defect prob per unit when sealer is stable
    drift_every=5_000,     # avg units between drift events (nozzle clog, path shift)
    p_drift=0.25,          # defect prob per unit while drifting
    final_det=0.85,        # manual visual detection at final inspection
    scrap_late=0.30,       # share of late-found defects that are scrapped (after paint/assembly)
    scrap_early=0.05,      # share of defects found right after sealer that are still scrapped
    coverage=0.70,         # share of sealer defect modes an in-line AI camera can see
    late_dist=300,         # units between sealer and today's final inspection
    late_lag=150,          # units built before manual feedback reaches the sealer
    sealer_share=0.40,     # share of plant scrap that comes from the pilot scope (team assumption)
)
SCEN = {
    # name: (in-line check?, final-inspection detection, in-line detection, episodes where alerts are dismissed)
    "1. Today: visual at final inspection, manual feedback": (False, 0.85, 0.0, 0.0),
    "2. Better camera at end-of-line only (tech, no loop)": (False, 0.95, 0.0, 0.0),
    "3. Closed loop at sealer, 31% of alerts dismissed (as today)": (True, 0.85, 0.90, 0.31),
    "4. Closed loop with people-centred design (10% dismissed)": (True, 0.85, 0.90, 0.10),
}
REPS = 300
H = 6_000  # max units simulated per drift episode
NEAR_DIST, NEAR_LAG = 5, 10  # in-line check right after sealer, automatic feedback


def run_scenario(inline, final_det, ai_det, dismiss, p=QP, reps=REPS, units=UNITS):
    """Episode-based simulation of sealer drift. Returns per-run [defects, scrapped, escaped, drift units]."""
    out = np.zeros((reps, 4))
    for r in range(reps):
        n_ep = rng.poisson(units / p["drift_every"])
        defects = scrapped = escaped = drift_units = 0.0
        for _ in range(n_ep):
            idxs = np.flatnonzero(rng.random(H) < p["p_drift"])
            loop_on = inline and rng.random() >= dismiss
            final_hit = rng.random(idxs.size) < final_det
            if loop_on:
                ai_hit = (rng.random(idxs.size) < p["coverage"]) & (rng.random(idxs.size) < ai_det)
                trig_hits, dist, lag = ai_hit, NEAR_DIST, NEAR_LAG
            else:
                ai_hit = np.zeros(idxs.size, bool)
                trig_hits, dist, lag = final_hit, p["late_dist"], p["late_lag"]
            fix = min(H, idxs[np.argmax(trig_hits)] + dist + lag) if trig_hits.any() else H
            m = idxs < fix
            early = ai_hit[m]; late = (~early) & final_hit[m]; esc = (~early) & (~final_hit[m])
            defects += m.sum(); escaped += esc.sum(); drift_units += fix
            scrapped += early.sum() * p["scrap_early"] + late.sum() * p["scrap_late"]
        nd = rng.binomial(int(max(units - drift_units, 0)), p["p_normal"])
        ef = rng.binomial(nd, p["coverage"] * ai_det) if inline else 0
        lf = rng.binomial(nd - ef, final_det)
        out[r] = (defects + nd, scrapped + ef * p["scrap_early"] + lf * p["scrap_late"],
                  escaped + nd - ef - lf, drift_units)
    return out


qres = {}
for name, args in SCEN.items():
    o = run_scenario(*args)
    qres[name] = dict(def_mean=o[:, 0].mean(), scrap_mean=o[:, 1].mean(), esc_mean=o[:, 2].mean(),
                      drift_mean=o[:, 3].mean(), scrap_p5=np.percentile(o[:, 1], 5), scrap_p95=np.percentile(o[:, 1], 95))
base_scrap = qres[list(SCEN)[0]]["scrap_mean"]
base_esc = qres[list(SCEN)[0]]["esc_mean"]
for v in qres.values():
    v["scrap_red"] = 1 - v["scrap_mean"] / base_scrap
    v["esc_red"] = 1 - v["esc_mean"] / base_esc

# sensitivity of closed-loop (scenario 4) scrap reduction to key unknowns
sens_q = []
for label, key, vals in [("AI camera coverage of defect modes", "coverage", [0.50, 0.70, 0.90]),
                         ("Drift defect rate", "p_drift", [0.10, 0.25, 0.40]),
                         ("Units between drift events", "drift_every", [2_500, 5_000, 10_000]),
                         ("Late-found scrap share", "scrap_late", [0.15, 0.30, 0.50]),
                         ("Units from sealer to today's inspection", "late_dist", [100, 300, 600])]:
    row = [label]
    for v in vals:
        p2 = dict(QP); p2[key] = v
        o_today = run_scenario(*SCEN[list(SCEN)[0]], p=p2, reps=120)
        o_cl = run_scenario(*SCEN[list(SCEN)[3]], p=p2, reps=120)
        row.append((v, 1 - o_cl[:, 1].mean() / o_today[:, 1].mean()))
    sens_q.append(row)
dismiss_curve = []
for dis in (0.0, 0.10, 0.20, 0.31, 0.50):
    o_cl = run_scenario(True, 0.85, 0.90, dis, reps=150)
    dismiss_curve.append((dis, 1 - o_cl[:, 1].mean() / base_scrap))

# ------------------------------------------------------------------ 2. FINANCIAL MONTE CARLO
CC = 250_000 * 0.70 * 3.2 / 1000
SPLIT = dict(labor=0.40, energy=0.12, maint=0.13, dep=0.25, scrap=0.10)
r_, g_ = 0.10, 0.04
RAMP = np.array([0.10, 0.35, 0.65, 0.90, 1.00])
PHASE = np.array([0.10, 0.15, 0.40, 0.25, 0.10])        # pilot-light, matches Assumptions row 44
PHASE_FRONT = np.array([0.30, 0.35, 0.25, 0.10, 0.0])   # original front-loaded phasing
t = np.arange(1, 6)


def npv_model(scrap, maint, nva, energy, var, inv, runp, train, nvar=3, cvar=10, real=0.5, adopt=1.0, labor=0.40):
    run_rate = CC * (SPLIT["scrap"] * scrap + SPLIT["maint"] * maint + labor * 0.22 * nva * real + SPLIT["energy"] * energy) + nvar * cvar * var
    sav = run_rate * RAMP * adopt * (1 + g_) ** (t - 1)
    invest = inv * PHASE
    running = np.cumsum(invest) * runp + train
    net = sav - invest - running
    return (net / (1 + r_) ** t).sum(), net, run_rate


BASE = dict(scrap=0.35, maint=0.10, nva=0.30, energy=0.05, var=0.35, inv=80, runp=0.10, train=2.5)
base_npv, base_net, base_rr = npv_model(**BASE)

N = 10_000
tri = lambda lo, mode, hi: rng.triangular(lo, mode, hi, N)
draws = dict(scrap=tri(0.20, 0.35, 0.50), maint=tri(0.05, 0.10, 0.15), nva=tri(0.15, 0.30, 0.45),
             energy=tri(0.02, 0.05, 0.08), var=tri(0.20, 0.35, 0.50), inv=tri(60, 80, 110),
             runp=tri(0.08, 0.09, 0.12), train=tri(2.0, 2.5, 3.0), nvar=tri(2, 3, 5), cvar=tri(5, 10, 15),
             real=tri(0.3, 0.5, 0.7), adopt=tri(0.6, 1.0, 1.0), labor=tri(0.35, 0.40, 0.45))
npvs = np.empty(N); rrs = np.empty(N)
for i in range(N):
    npvs[i], _, rrs[i] = npv_model(**{k: v[i] for k, v in draws.items()})
mc = dict(mean=npvs.mean(), p5=np.percentile(npvs, 5), p50=np.median(npvs), p95=np.percentile(npvs, 95),
          prob_pos=(npvs > 0).mean(), rr_p50=np.median(rrs), rr_pct_p50=np.median(rrs) / CC)
hist_counts, hist_edges = np.histogram(npvs, bins=16)

# Roadmap design test. Strategy variants run on the same 10,000 uncertainty draws.
GATE_ADOPT = 0.80                                     # pilot adoption needed to pass the end-2027 gate
PHASE_LIGHT = PHASE
PILOT_RAMP = np.array([0.10, 0.35, 0.35, 0.35, 0.35])   # if gate fails: keep pilot-scope savings only


RAMP_SLOW = np.array([0.05, 0.15, 0.40, 0.70, 0.95])  # savings arrive ~1 year later than plan


def npv_strategy(phase, gate=False, residual=False, ramp=None, **kw):
    adopt = kw.get("adopt", 1.0)
    run_rate = npv_model(**kw)[2]
    stop = gate and adopt < GATE_ADOPT
    base_ramp = RAMP if ramp is None else ramp
    ramp = np.minimum(PILOT_RAMP, base_ramp) if stop else base_ramp
    invest = kw["inv"] * phase * (np.array([1, 1, 0, 0, 0]) if stop else 1)
    sav = run_rate * ramp * adopt * (1 + g_) ** (t - 1)
    net = sav - invest - (np.cumsum(invest) * kw["runp"] + kw["train"])
    pv = (net / (1 + r_) ** t).sum()
    if residual:  # remaining book value of equipment at end-2030 (5-year straight line, bought mid-year)
        rem = np.clip((t - 0.5) / 5, 0, 1)
        pv += (invest * rem).sum() / (1 + r_) ** 5
    return pv


def run_mc(**opts):
    v = np.array([npv_strategy(**opts, **{k: d[i] for k, d in draws.items()}) for i in range(N)])
    return dict(mean=v.mean(), p5=np.percentile(v, 5), p50=np.median(v), p95=np.percentile(v, 95), prob_pos=(v > 0).mean())


strategies = [
    ("A. Front-loaded phasing, no gate", dict(phase=PHASE_FRONT)),
    ("B. Front-loaded phasing + gate (65% already spent)", dict(phase=PHASE_FRONT, gate=True)),
    ("C. Pilot-light phasing, no gate (as in Model tab)", dict(phase=PHASE_LIGHT)),
    ("D. Pilot-light phasing + gate", dict(phase=PHASE_LIGHT, gate=True)),
    ("E. D + remaining equipment life valued at book", dict(phase=PHASE_LIGHT, gate=True, residual=True)),
    ("F. D but savings ramp one year slower (stress test)", dict(phase=PHASE_LIGHT, gate=True, ramp=RAMP_SLOW)),
    ("G. F + remaining equipment life valued at book", dict(phase=PHASE_LIGHT, gate=True, ramp=RAMP_SLOW, residual=True)),
]
strat_res = [(name, run_mc(**o)) for name, o in strategies]
gate_stop_share = (draws["adopt"] < GATE_ADOPT).mean()
assert abs(strat_res[2][1]["mean"] - mc["mean"]) < 1e-6  # variant C must reproduce the main Monte Carlo

# ------------------------------------------------------------------ 3. TORNADO
tor_spec = [("Scrap reduction", "scrap", 0.20, 0.50), ("Maintenance reduction", "maint", 0.05, 0.15),
            ("Operator NVA eliminated", "nva", 0.15, 0.45), ("Energy reduction", "energy", 0.02, 0.08),
            ("Variant cost reduction", "var", 0.20, 0.50), ("Investment (Rp B)", "inv", 110, 60),
            ("Running cost %", "runp", 0.12, 0.08), ("Adoption achieved", "adopt", 0.6, 1.0),
            ("Variant projects / yr", "nvar", 2, 5), ("Cost per variant project", "cvar", 5, 15)]
tornado = []
for lab, key, lo, hi in tor_spec:
    a = npv_model(**{**BASE, key: lo})[0]; b = npv_model(**{**BASE, key: hi})[0]
    tornado.append((lab, lo, hi, a, b, abs(b - a)))
tornado.sort(key=lambda x: -x[5])

# ------------------------------------------------------------------ WRITE TO WORKBOOK
F = "Arial"
B = Font(name=F, bold=True, size=10); N_ = Font(name=F, size=10); BL = Font(name=F, size=10, color="0000FF")
T = Font(name=F, bold=True, size=14, color="1F3864"); H2 = Font(name=F, bold=True, size=10, color="FFFFFF")
HF = PatternFill("solid", fgColor="1F3864"); KEY = PatternFill("solid", fgColor="E2EFDA")
W = Alignment(wrap_text=True, vertical="top"); th = Side(style="thin", color="BFBFBF"); BOX = Border(th, th, th, th)
PCT = '0.0%;(0.0%);"-"'; RP = '#,##0.0;(#,##0.0);"-"'; INT = '#,##0'

wb = load_workbook("TMMIN_Case_Model.xlsx")
s = wb.create_sheet("Simulation", 4)


def w(ref, v, font=N_, fmt=None, fill=None, wrap=False):
    c = s[ref]; c.value = v; c.font = font
    if fmt: c.number_format = fmt
    if fill: c.fill = fill
    if wrap: c.alignment = W
    return c


def hdr(row, labels):
    for i, lab in enumerate(labels):
        c = s.cell(row=row, column=1 + i, value=lab); c.font = H2; c.fill = HF; c.alignment = W; c.border = BOX


w("A1", "Idea tests: simulation results (values produced by run_tests.py, not formulas)", T)
w("A2", "Re-run run_tests.py after changing assumptions. Process parameters below are illustrative assumptions, not TMMIN data: present them as a mechanism test, and show the sensitivity.", N_)

r = 4
w(f"A{r}", "TEST 1. Does closing the quality loop beat adding technology alone? (sealer drift -> inspection -> feedback, 1 year, 175,000 units, 300 runs)", B); r += 1
hdr(r, ["Scenario", "Defective units / yr", "Scrapped units / yr", "Escaped defects / yr", "Units built while drifting", "Scrap vs today", "Escapes vs today", "Scrap P5-P95"]); r += 1
q_first = r
for name, v in qres.items():
    vals = [name, v["def_mean"], v["scrap_mean"], v["esc_mean"], v["drift_mean"], -v["scrap_red"], -v["esc_red"],
            f"{v['scrap_p5']:,.0f} - {v['scrap_p95']:,.0f}"]
    for j, val in enumerate(vals):
        c = s.cell(row=r, column=1 + j, value=val); c.font = B if j == 0 else N_; c.border = BOX
        c.number_format = PCT if j in (5, 6) else INT
        if j == 0: c.alignment = W
    if name.startswith("4"):
        for j in range(8): s.cell(row=r, column=1 + j).fill = KEY
    r += 1
cl = qres[list(SCEN)[3]]; ai = qres[list(SCEN)[1]]; ig = qres[list(SCEN)[2]]
plant_wide = cl["scrap_red"] * QP["sealer_share"]
r += 1
w(f"A{r}", "What this shows", B); r += 1
for line in [
    f"- A better camera at end-of-line alone changes scrap by {-ai['scrap_red']:+.0%} while escapes fall {ai['esc_red']:.0%}: it catches more bad units, but too late, so escapes turn into scrap. It does not prevent defects.",
    f"- Closing the loop right after the sealer cuts scrap {cl['scrap_red']:.0%} and escapes {cl['esc_red']:.0%}, because a drift is stopped within a few units instead of hundreds.",
    f"- If operators dismiss alerts in 31% of drift episodes (today's override rate), scrap reduction falls to {ig['scrap_red']:.0%}. Trust, training and alert design are part of the value, not an add-on.",
    f"- Plant-wide: if the pilot scope causes {QP['sealer_share']:.0%} of plant scrap (team assumption), the plant-wide scrap cut is about {plant_wide:.0%}. Compare with the 20% / 35% / 50% lever in Assumptions.",
    "- Deck message: value comes from redesigning the system (where the check sits, how fast the signal travels, who acts on it), not from buying the device. That is exactly the case ask.",
]:
    w(f"A{r}", line, N_, wrap=True); s.row_dimensions[r].height = 28; r += 1
r += 1
w(f"A{r}", "Process assumptions used (illustrative, change and re-run)", B); r += 1
for k, lab in [("p_normal", "Defect probability per unit, stable sealer"), ("drift_every", "Average units between drift events"),
               ("p_drift", "Defect probability per unit while drifting"), ("final_det", "Manual visual detection rate at final inspection"),
               ("coverage", "Share of sealer defect modes the in-line AI camera can see"),
               ("late_dist", "Units between sealer and today's final inspection"), ("late_lag", "Units built before manual feedback reaches the sealer"),
               ("scrap_late", "Share of late-found defects scrapped"), ("scrap_early", "Share of early-found defects scrapped"),
               ("sealer_share", "Share of plant scrap from the pilot scope (team assumption)")]:
    w(f"A{r}", lab); w(f"B{r}", QP[k], BL, PCT if QP[k] < 1 else INT); r += 1
w(f"A{r}", f"In-line check: {NEAR_DIST} units after sealer, automatic feedback within {NEAR_LAG} units, 90% detection on visible defect modes (case: AI camera in validation to Oct 2026).", N_, wrap=True)
s.row_dimensions[r].height = 28; r += 2
w(f"A{r}", "Robustness: closed-loop (scenario 4) scrap reduction vs today when each assumption changes", B); r += 1
hdr(r, ["Assumption", "Low", "Reduction", "Base", "Reduction", "High", "Reduction"]); r += 1
for row in sens_q:
    s.cell(row=r, column=1, value=row[0]).font = B
    for j, (v, red) in enumerate(row[1:]):
        c1 = s.cell(row=r, column=2 + 2 * j, value=v); c1.font = BL; c1.number_format = PCT if v < 1 else INT
        c2 = s.cell(row=r, column=3 + 2 * j, value=red); c2.number_format = PCT; c2.font = N_
    r += 1
mins = min(min(x[1] for x in row[1:]) for row in sens_q)
w(f"A{r}", f"Lowest scrap reduction across all tested cases: {mins:.0%}. The mechanism holds even with pessimistic process assumptions.", B); r += 2
w(f"A{r}", "People test: how much value is lost when operators dismiss alerts?", B); r += 1
hdr(r, ["Share of drift episodes where alerts are dismissed", "Scrap reduction vs today"]); r += 1
d_first = r
for dis, red in dismiss_curve:
    w(f"A{r}", dis, BL, PCT); w(f"B{r}", red, N_, PCT); r += 1
ch3 = BarChart(); ch3.type = "col"; ch3.title = "Scrap reduction falls as alerts are dismissed"; ch3.legend = None
ch3.add_data(Reference(s, min_col=2, min_row=d_first, max_row=r - 1), titles_from_data=False)
ch3.set_categories(Reference(s, min_col=1, min_row=d_first, max_row=r - 1)); ch3.height = 6; ch3.width = 12
ch3.y_axis.numFmt = "0%"
s.add_chart(ch3, f"D{d_first-1}")
w(f"A{r}", "Exhibit 6B says 31% of operators frequently override alerts today. This chart is the quantified case for the people part of the idea.", N_, wrap=True)
s.row_dimensions[r].height = 28; r += 2

w(f"A{r}", "TEST 2. Is the business case robust? Financial Monte Carlo (10,000 runs, mirrors the Model tab incl. pilot-light phasing)", B); r += 1
hdr(r, ["Metric", "Value", "Note"]); r += 1
for lab, val, fmt, note in [
    ("Deterministic base NPV (check vs Model tab)", base_npv, RP, "Should match Dashboard base NPV"),
    ("Mean NPV", mc["mean"], RP, "Rp billion"),
    ("P5 NPV (bad case)", mc["p5"], RP, "1-in-20 downside"),
    ("Median NPV", mc["p50"], RP, ""),
    ("P95 NPV (good case)", mc["p95"], RP, ""),
    ("Probability NPV > 0", mc["prob_pos"], PCT, "Headline for the financial slide"),
    ("Median full run-rate savings (Rp B/yr)", mc["rr_p50"], RP, ""),
    ("Median run-rate as % of conversion cost", mc["rr_pct_p50"], PCT, "vs 16% gap to benchmark"),
]:
    w(f"A{r}", lab, B); w(f"B{r}", val, N_, fmt); w(f"C{r}", note); r += 1
r += 1
w(f"A{r}", f"TEST 2b. How should the roadmap spend the money? Same 10,000 runs, five strategies (gate = stop scaling if 2027 pilot adoption < {GATE_ADOPT:.0%}; happens in {gate_stop_share:.0%} of runs)", B); r += 1
hdr(r, ["Strategy", "Mean NPV", "P5 NPV", "Median NPV", "P95 NPV", "P(NPV > 0)"]); r += 1
best = strat_res[3][0]
for name, res in strat_res:
    vals = [name, res["mean"], res["p5"], res["p50"], res["p95"], res["prob_pos"]]
    for j, val in enumerate(vals):
        c = s.cell(row=r, column=1 + j, value=val); c.border = BOX; c.font = B if j == 0 else N_
        c.number_format = PCT if j == 5 else RP
        if name == best: c.fill = KEY
    r += 1
pl = PHASE_LIGHT
w(f"A{r}", f"Pilot-light phasing: {pl[0]:.0%} / {pl[1]:.0%} / {pl[2]:.0%} / {pl[3]:.0%} / {pl[4]:.0%} of capex in 2026-2030. Ramp-up kept the same to isolate the effect of phasing; if scaling later also delays savings, the gain is smaller.", N_, wrap=True)
s.row_dimensions[r].height = 30; r += 1
w(f"A{r}", f"Reading: a gate only protects value if little money is spent before it. Gate after heavy spending (B) destroys value; pilot-light + gate (D) is the design to defend in SQ3. Valuing equipment life beyond 2030 (E) is legitimate but state it openly. Stress test (F): if savings arrive a year late, P(NPV>0) falls to {strat_res[5][1]['prob_pos']:.0%} ({strat_res[6][1]['prob_pos']:.0%} if remaining equipment life is valued, G). Speed of the pilot is the make-or-break factor: quick wins in 2026-27 belong in the roadmap.", B, wrap=True)
s.row_dimensions[r].height = 58; r += 1
w(f"A{r}", "Ranges used (triangular low / mode / high): scrap 20/35/50%, maintenance 5/10/15%, NVA 15/30/45%, energy 2/5/8%, variant cost 20/35/50%, investment 60/80/110, running 8/9/12%, training 2/2.5/3, variant projects 2/3/5, cost per project 5/10/15, cash realization 30/50/70%, adoption 60/100/100%, labor share 35/40/45%.", N_, wrap=True)
s.row_dimensions[r].height = 45; r += 2
w(f"A{r}", "NPV distribution (histogram)", B); r += 1
hdr(r, ["NPV bin from (Rp B)", "Runs"]); r += 1
h_first = r
for c_, e in zip(hist_counts, hist_edges[:-1]):
    w(f"A{r}", round(float(e), 1), N_, RP); w(f"B{r}", int(c_), N_, INT); r += 1
h_last = r - 1
ch = BarChart(); ch.type = "col"; ch.title = "NPV across 10,000 runs (Rp B)"; ch.legend = None
ch.add_data(Reference(s, min_col=2, min_row=h_first, max_row=h_last), titles_from_data=False)
ch.set_categories(Reference(s, min_col=1, min_row=h_first, max_row=h_last)); ch.height = 7; ch.width = 16; ch.gapWidth = 10
s.add_chart(ch, f"E{h_first-1}")
r += 1
w(f"A{r}", "TEST 3. Which assumption matters most? Tornado (base case, one at a time)", B); r += 1
hdr(r, ["Driver", "Low input", "High input", "NPV at low", "NPV at high", "Swing"]); r += 1
for lab, lo, hi, a, b_, sw in tornado:
    vals = [lab, lo, hi, a, b_, sw]
    for j, val in enumerate(vals):
        c = s.cell(row=r, column=1 + j, value=val); c.border = BOX; c.font = B if j == 0 else N_
        c.number_format = RP if j >= 3 else (PCT if isinstance(val, float) and val < 1 else '0.0')
    r += 1
w(f"A{r}", "Use the top 2-3 drivers as the assumptions you defend hardest in Q&A, and as the KPIs you track first in the pilot.", B)
for col, wd in zip("ABCDEFGH", (62, 18, 18, 18, 20, 14, 14, 16)):
    s.column_dimensions[col].width = wd

wb.save("TMMIN_Case_Model.xlsx")

print("base NPV", round(base_npv, 2), "run-rate", round(base_rr, 1))
for k, v in qres.items():
    print(k, {kk: round(vv, 3) for kk, vv in v.items()})
print("sens", [(row[0], [(v, round(x, 3)) for v, x in row[1:]]) for row in sens_q])
print("dismiss", [(d_, round(x, 3)) for d_, x in dismiss_curve])
print("MC", {k: round(v, 3) for k, v in mc.items()})
for name, res in strat_res:
    print("STRAT", name, {k: round(v, 2) for k, v in res.items()})
print("gate stop share", gate_stop_share)
print("tornado", [(x[0], round(x[3], 1), round(x[4], 1)) for x in tornado])
