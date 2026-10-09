"""Stage 2 diagnosis numbers. Run: python work/2_diagnosis_calc.py

Every input is a casebook exhibit (data/facts.md) or a team assumption already
used in model/build_model.py (cost split). Assumptions are labelled ASSUMPTION.
"""
import math
from itertools import product

# ---- Exhibit 3: conversion cost index (TMMIN 2023 = 100)
tmmin = {2023: 100, 2024: 103, 2025: 106}
new = {2023: 94, 2024: 91, 2025: 89}

print("== 1. Gap trajectory (Exhibit 3)")
for y in tmmin:
    pts = tmmin[y] - new[y]
    print(f"  {y}: gap {pts:>2} pts, TMMIN {tmmin[y] / new[y] - 1:5.1%} more expensive")
widen = ((tmmin[2025] - new[2025]) - (tmmin[2023] - new[2023])) / 2
print(f"  Gap widens {widen:.1f} pts/yr on average")
log_t = math.log(tmmin[2025] / tmmin[2023])
log_n = math.log(new[2025] / new[2023])
share_t = log_t / (log_t - log_n)
print(f"  Widening 2023-25 from TMMIN rising: {share_t:.0%}; from new player falling: {1 - share_t:.0%}")
gap_2030 = (tmmin[2025] - new[2025]) + widen * 5
print(f"  ILLUSTRATIVE straight-line do-nothing gap 2030: ~{gap_2030:.0f} pts")
new_2030 = new[2025] - (new[2023] - new[2025]) / 2 * 5
print(f"  ILLUSTRATIVE new player index 2030 if it keeps falling 2.5 pts/yr: ~{new_2030:.0f}")

# ---- Cost bridge 2023 -> 2025 for TMMIN
# ASSUMPTION: cost split as in model/build_model.py (case lists components only)
split = {"labor": 0.40, "energy": 0.12, "maintenance": 0.13, "depreciation": 0.25, "scrap": 0.10}
esc = 0.04                      # Exhibit 9
print("\n== 2. Bridge of TMMIN index 100 -> 106 (ASSUMPTIONS: index nominal, cost split from model)")
p_esc = (split["labor"] + split["energy"]) * ((1 + esc) ** 2 - 1) * 100
p_scrap = split["scrap"] * (108 / 100 - 1) * 100                      # Exhibit 4 scrap index
p_nva = split["labor"] * ((1 - 0.20) / (1 - 0.22) - 1) * 100          # Exhibit 4 NVA 20% -> 22%
p_maint_hi = split["maintenance"] * (111 / 100 - 1) * 100             # if maint. cost tracked downtime fully
print(f"  Labor+energy escalation 4%/yr : +{p_esc:.1f} pts")
print(f"  Scrap index 100 -> 108         : +{p_scrap:.1f} pts")
print(f"  NVA 20% -> 22% (more hours)    : +{p_nva:.1f} pts")
print(f"  Downtime 100 -> 111 (0 to full): +0.0 to +{p_maint_hi:.1f} pts")
lo, hi = p_esc + p_scrap + p_nva, p_esc + p_scrap + p_nva + p_maint_hi
print(f"  Explained: +{lo:.1f} to +{hi:.1f} pts vs observed +6.0")
drift_lo, drift_hi = p_scrap + p_nva, p_scrap + p_nva + p_maint_hi
gap25 = tmmin[2025] - new[2025]
print(f"  Performance drift (controllable): {drift_lo:.1f}-{drift_hi:.1f} pts = "
      f"{drift_lo / gap25:.0%}-{drift_hi / gap25:.0%} of the 17-pt gap")

print("\n== 3. Implied productivity (ASSUMPTION: new player faces the same escalation)")
real_t = tmmin[2025] / tmmin[2023] / (1 + p_esc / 100) - 1
real_n = new[2025] / new[2023] / (1 + p_esc / 100) - 1
print(f"  TMMIN real cost/unit 2023-25: {real_t:+.1%} ({(1 + real_t) ** 0.5 - 1:+.1%}/yr)")
print(f"  New player real cost/unit   : {real_n:+.1%} ({(1 + real_n) ** 0.5 - 1:+.1%}/yr)")

print("\n== 4. Improvement engine (Exhibit 6A)")
impl23, impl25 = 3.1 * 0.35, 2.4 * 0.28
print(f"  Implemented ideas/engineer/yr: {impl23:.2f} -> {impl25:.2f} ({impl25 / impl23 - 1:+.0%})")
y23, y25 = impl23 / 28, impl25 / 25
print(f"  Implemented ideas per % of time on improvement: {y23:.4f} -> {y25:.4f} ({y25 / y23 - 1:+.0%})")
print(f"  Time on improvement: 28% -> 25% ({25 / 28 - 1:+.0%})")

print("\n== 5. Capability (Exhibit 7, L3+ of 30)")
for f, l3, l4 in [("Mechanical", 14, 5), ("Electrical", 11, 4), ("PLC", 9, 3),
                  ("Programming", 5, 1), ("Software & AI", 2, 0)]:
    print(f"  {f:<14} {l3 + l4:>2}/30 = {(l3 + l4) / 30:4.0%}")

print("\n== 6. Survey (Exhibit 6B, N=120 pilot area)")
print(f"  See tech as helper 54% vs trained on data tools 18% -> readiness gap {54 - 18} pts")
print(f"  Idle capacity Karawang I+II: {250000 * (1 - 0.70):,.0f} units/yr (Exhibit 9)")

# ---- Gap heat map. Scores are TEAM JUDGMENT, one-line reason each in 2_diagnosis.md.
# (level, cost, quality, flexibility); impact 1 low .. 3 high
procs = {
    "Press shop":                  (3, 2, 2, 2),
    "Casting":                     (2, 2, 2, 1),
    "Machining & engine assembly": (3, 2, 2, 2),
    "Spot welding":                (3, 1, 1, 2),
    "Sealer":                      (2, 3, 3, 1),
    "Painting":                    (3, 2, 3, 1),
    "Final assembly":              (2, 3, 2, 3),
    "Quality inspection":          (1, 3, 3, 1),
    "Intralogistics":              (2, 3, 1, 2),
    "Maintenance":                 (2, 3, 1, 1),
    "Equipment & system integr.":  (2, 2, 1, 3),
    "Data integration":            (1, 2, 2, 3),
}


def score(v, w):
    lvl, c, q, f = v
    return (w[0] * c + w[1] * q + w[2] * f) * (4 - lvl)


print("\n== 7. Heat map priority = (cost + quality + flex) x (4 - level)")
base_w = (1, 1, 1)
ranked = sorted(procs, key=lambda p: -score(procs[p], base_w))
for p in ranked:
    print(f"  {p:<28} L{procs[p][0]}  score {score(procs[p], base_w):>2}")

print("\n== 8. Robustness: rank under every weighting with weights in {1,2,3}")
top3_count = {p: 0 for p in procs}
weights = list(product([1, 2, 3], repeat=3))
for w in weights:
    order = sorted(procs, key=lambda p: -score(procs[p], w))
    for p in order[:3]:
        top3_count[p] += 1
for p, n in sorted(top3_count.items(), key=lambda kv: -kv[1]):
    if n:
        print(f"  {p:<28} in top 3 for {n}/{len(weights)} weightings")

print("\n== 9. Between-process links (upstream process score + where the signal lands)")
links = [("Sealer", "Quality inspection"), ("Final assembly", "Quality inspection"),
         ("Painting", "Quality inspection"), ("Intralogistics", "Final assembly"),
         ("Maintenance", "Data integration"), ("Equipment & system integr.", "Data integration")]
for a, b in sorted(links, key=lambda l: -(score(procs[l[0]], base_w) + score(procs[l[1]], base_w))):
    print(f"  {a} -> {b}: {score(procs[a], base_w) + score(procs[b], base_w)}")
