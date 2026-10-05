"""System dynamics model of Closed-Loop Kaizen: mechanism, economics, sustainability.

Run:  python sd_model.py            (scenarios + Monte Carlo + charts + checks)
      python sd_model.py --quick    (skip Monte Carlo and charts)

What it is: a stock-and-flow model (Euler, monthly step, 2023-2035) of why the
plant stopped improving and what each policy does to that. It is calibrated to
the 2023 -> 2025 movements in Exhibits 4 and 6A, which are dummy data. Its job
is to compare policies and expose feedback (worse-before-better, tipping,
durability), not to forecast TMMIN to the decimal.

Stocks
  P   open problem pool (recurring abnormalities), 2023 = 1
  Q   improvement capability: erodes when improvement time sits below its norm
      (the capability trap, Repenning & Sterman 2001), rebuilds slowly above it
  K   share of critical know-how documented (Ex.6A)
  L1, L2, L3  Software & AI engineers by level (Ex.7)
  Tr  operator alert compliance = 1 - dismiss rate (Ex.6B: 31% dismiss)
  Lq  quality-loop coverage of vehicle lines
  Ld  data/interface standard coverage of processes

Every number below is either an exhibit, a parameter shared with build_model.py,
a cited external figure, or labelled ASSUMPTION / CALIBRATED.
"""
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
DT = 1 / 12
T0, T_END = 2023.0, 2036.0
STEPS = int(round((T_END - T0) / DT))
YEARS = list(range(2023, 2036))

# ---------------------------------------------------------------- case facts
FACT = dict(
    conv_cost_2025=560.0,      # Rp B, Ex.9 (175,000 units x Rp3.2M)
    disc=0.10, esc=0.04, life=5,  # Ex.9
    idx_2025=106, bench_2025=89, bench_2023=94,  # Ex.3
)
# Shared with build_model.py (ASSUMPTION there too: the case lists components only)
SPLIT = dict(labor=0.40, energy=0.12, maint=0.13, dep=0.25, scrap=0.10)

# ---------------------------------------------------------------- parameters
BASE = dict(
    # problem pool
    phi=1.07,            # ASSUMPTION: ~30% of open problems resolved per year in 2023
    p_min=0.85,          # ASSUMPTION: 15% of the 2023 pool is the most root-cause work can remove (irreducible rest)
    x_cap=2.0,           # ASSUMPTION: improvement productivity can at most double vs 2023
    gen0=None,           # CALIBRATED: P 1.00 -> 1.08 (scrap index, Ex.4)
    cplx_pre=0.0625,     # CALIBRATED: variant months 8 -> 9 (Ex.4) = complexity +6.25%/yr
    cplx_post=0.03125,   # ASSUMPTION: half that rate after 2025 (MC 0 to full rate)
    std_prevent=0.20,    # ASSUMPTION: a common interface standard prevents 20% of new integration problems
    unserved_gen=0.5,    # ASSUMPTION: fires left unserved breed 50% more problems (worse-before-better)
    phi_ff=1.0,          # ASSUMPTION: firefighting clears symptoms as fast as improvement clears causes...
    recur=0.80,          # ASSUMPTION: ...but 80% of symptom fixes come back (Repenning & Sterman 2001)
    # engineer time
    r0=0.62, r_exp=0.50, other=0.10,  # Ex.6A 62% routine, 28% improvement; r_exp CALIBRATED to 65%
    k_routine=0.6,       # ASSUMPTION: documented know-how shortens troubleshooting
    tool_routine=0.15,   # ASSUMPTION: citizen tools absorb up to 15% of routine work
    r_floor=0.45,        # build_model.py Capability tab: some routine work always remains
    r_cap=0.75,          # ASSUMPTION: above 75% management adds overtime/contractors (not costed: flatters do-nothing)
    # capability trap
    i_norm=0.30,         # ASSUMPTION: improvement share needed just to hold capability
    erode=None,          # CALIBRATED: implemented ideas/engineer 1.08 -> 0.67 (Ex.6A)
    build=0.40,          # ASSUMPTION: rebuilding is slower than eroding
    q_floor=0.50, q_max=1.30,  # ASSUMPTION: capability erodes toward half, not to zero
    # productivity multipliers
    tools_gain=0.50,     # ASSUMPTION: 12 extra L3+ engineers' tools lift output 50% (Toyota AI Platform shows scale, not a %)
    vis_gain=0.50,       # ASSUMPTION: a closed loop makes causes visible, +50% fix productivity at full coverage
    idea_gain=0.25,      # ASSUMPTION: operator idea engine adds 25% (62% willing, Ex.6B)
    # knowledge
    kc=None,             # CALIBRATED: documented know-how 35% -> 33% (Ex.6A)
    k_decay=0.10,        # ASSUMPTION: 10%/yr of documented know-how goes stale (variants, retirements)
    k_std_gain=1.5,      # ASSUMPTION: with the loop, each fix is written into standard work
    sprint=0.12,         # ASSUMPTION: capture sprints with seniors, share of the undocumented gap per yr
    # capability pipeline (same rates as build_model.py Capability tab)
    p12=-np.log(0.70), p23=-np.log(0.80),
    partner_build=0.15,  # ASSUMPTION: partner-built coverage/yr during the pilot, with knowledge transfer
    build_per_eng=0.06,  # ASSUMPTION: each L3+ engineer can extend loop coverage 6 pts/yr
    # operators
    tr0=0.69,            # Ex.6B: 31% dismiss alerts
    tr_hc=0.90,          # ASSUMPTION: co-designed, explain-why alerts reach 10% dismiss (team target)
    tr_tau=0.75,
    fatigue=0.15,        # ASSUMPTION: more alerts with no loop -> compliance falls 15 pts at full coverage
    # lever effects (shared ranges with build_model.py / research.md)
    scope=0.40,          # share of plant scrap the quality loop can reach (build_model.py base)
    loop_eff=0.939,      # own discrete sim (run_tests.py): in-scope scrap cut at 0% dismiss, linear in compliance
    esc_eff=0.95,        # own sim: escapes cut ~86% at 10% dismiss
    cam_scrap=0.117,     # own sim: better end-of-line camera alone raises scrap 11.7%
    cam_esc=0.667,       # own sim: ... and cuts escapes 67%
    dt_red=0.25,         # downtime cut at full data coverage (McKinsey up to 50%; IIoT World)
    maint_var=0.30,      # ASSUMPTION: 30% of maintenance cost moves with unplanned downtime
    nva_red=0.30,        # build_model.py base
    cash_conv=0.50,      # build_model.py: half of freed operator time becomes cash, rest -> kaizen
    e_red=0.05,          # build_model.py base (Nissan US 13.8%, CEM 2022)
    var_red=0.35,        # build_model.py base (Siemens/Wipro PARI 70%, Kalypso 40%)
    var_projects=3, var_cost=10.0,  # build_model.py: 3 projects/yr x Rp10B
    adopt=1.0,           # share of each lever's designed effect TMMIN actually realises (MC 60/100/100%, as run_tests.py)
    # program cost
    capex=80.0, run_pct=0.10, training=2.5,
    # sustainability (cited)
    tariff=1114.74,      # Rp/kWh, PLN I-3 industrial tariff 2025 (CNBC Indonesia, 3 Sep 2025)
    elec_share=0.70,     # ASSUMPTION: share of energy cost that is grid electricity (rest gas/fuel)
    grid_ef=0.80,        # tCO2/MWh, Jawa-Madura-Bali grid 2019 (Kepmen ESDM 163.K/HK.02/MEM.S/2021)
    carbon_tax=30.0,     # Rp/kgCO2e, UU 7/2021 (HPP) floor rate
)

PHASING = {2026: 0.10, 2027: 0.15, 2028: 0.40, 2029: 0.25, 2030: 0.10}   # pilot-light, build_model.py
FRONT = {2026: 0.30, 2027: 0.35, 2028: 0.25, 2029: 0.10, 2030: 0.0}
FAST = {2026: 0.10, 2027: 0.25, 2028: 0.40, 2029: 0.20, 2030: 0.05}    # pilot-light, gate mid-2027, quicker phase 2
START = 2026.75   # Q4 2026, after AI camera validation (Ex.5)

# ---------------------------------------------------------------- policies
POLICIES = {
    "do_nothing": dict(label="Tanpa tindakan"),
    "frozen_2025": dict(label="Kinerja dibekukan di 2025", frozen=True),
    "tech_only": dict(label="Beli teknologi saja", camera=True, capex=80.0, training=0.5),
    "people_only": dict(label="Program SDM saja", academy=True, ideas=True, firewall=True, ratchet=True,
                        sprints=True, capex=12.0, training=3.0),
    "clk_v1": dict(label="Closed-Loop Kaizen v1", loop=True, academy=True, ideas=True, sprints=True, hc=True),
    "clk_v2": dict(label="Closed-Loop Kaizen v2", loop=True, academy=True, ideas=True, sprints=True,
                   hc=True, firewall=True, ratchet=True),
    "clk_v2_hard": dict(label="CLK v2, lindungi 40%", loop=True, academy=True, ideas=True, sprints=True,
                        hc=True, firewall=True, protect=0.40),
    "clk_v2_fast": dict(label="CLK v2, gate pertengahan 2027", loop=True, academy=True, ideas=True,
                        sprints=True, hc=True, firewall=True, ratchet=True, phasing=FAST, gate_at=0.75),
    "clk_v2_front": dict(label="CLK v2, belanja di awal + gate", loop=True, academy=True, ideas=True,
                         sprints=True, hc=True, firewall=True, ratchet=True, phasing=FRONT),
    "clk_v2_late": dict(label="CLK v2, terlambat 1 tahun", loop=True, academy=True, ideas=True,
                        sprints=True, hc=True, firewall=True, ratchet=True, delay=1.0),
    "clk_v2_relapse": dict(label="CLK v2, program dihentikan 2031", loop=True, academy=True,
                           ideas=True, sprints=True, hc=True, firewall=True, ratchet=True, end=2031.0),
}


def firewall_level(t, pol):
    """Protected improvement share. CLK v2 protects the norm (30%) from the start;
    the ratchet in simulate() then locks in whatever the loops free on top.
    Protecting 35-40% was tested and dropped: it costs ~Rp3-4 B of 2026-30 NPV in
    unserved fires for little extra (see work/5_tests.md)."""
    s = START + pol.get("delay", 0.0)
    if not pol.get("firewall") or t < s or t >= pol.get("end", 99e9):
        return 0.0
    return pol.get("protect", 0.30) * min(1.0, (t - s) / 0.5)   # phased in over six months


def capex_target(t, pol, phasing):
    """Cumulative share of capex spent by time t (spent evenly within each year)."""
    shift = pol.get("delay", 0.0)
    cum = 0.0
    for y, sh in phasing.items():
        y0 = y + shift
        if t >= y0 + 1:
            cum += sh
        elif t > y0:
            cum += sh * (t - y0)
    return cum


def simulate(p, pol, phasing=PHASING, gate=True):
    """One run. Returns monthly arrays and annual aggregates."""
    phasing = pol.get("phasing", phasing)
    n = STEPS
    out = {k: np.zeros(n) for k in ("t", "P", "Q", "K", "S", "Tr", "Lq", "Ld", "R", "I", "ideas",
                                    "scrap", "esc", "down", "nva", "energy", "months", "cost_idx",
                                    "cost_idx_real", "u", "spent")}
    P, Q, K, Tr, Lq, Ld = 1.0, 1.0, 0.35, p["tr0"], 0.0, 0.0
    L1, L2, L3 = 20.0, 8.0, 2.0            # Ex.7 Software & AI (L3 includes L4)
    s = START + pol.get("delay", 0.0)
    stopped = False                         # go/no-go gate outcome
    frozen_share = None
    cam = 0.0                               # vendor camera coverage (tech-only)
    nva_2025 = None
    ratchet_hi = 0.0
    for i in range(n):
        t = T0 + i * DT
        on = s <= t < pol.get("end", 99e9)
        ended = t >= pol.get("end", 99e9)
        # complexity: calibrated trend to 2025, then the assumed post-2025 rate
        C = 1 + p["cplx_pre"] * min(t - T0, 2.0) + p["cplx_post"] * max(t - 2025.0, 0.0)
        S = L3
        tools = 1 + p["tools_gain"] * np.clip((S - 2) / 12, 0, 1.2)
        # engineer time
        routine = p["r0"] * P ** p["r_exp"] * (1 - p["k_routine"] * (K - 0.35)) \
            * (1 - p["tool_routine"] * np.clip((S - 2) / 12, 0, 1))
        demand = float(max(routine, p["r_floor"]))
        routine = float(np.clip(routine, p["r_floor"], p["r_cap"]))
        natural = 1 - p["other"] - routine
        prot = max(firewall_level(t, pol), ratchet_hi if (pol.get("ratchet") and on) else 0.0)
        I = max(natural, prot)
        if pol.get("ratchet") and on:      # lock in time the loop frees; never hand it back
            ratchet_hi = min(max(ratchet_hi, natural), 1 - p["other"] - p["r_floor"])
        u = max(0.0, I - natural) / routine          # share of fires left unserved
        # productivity of improvement work
        a = p["adopt"]
        vis = 1 + a * p["vis_gain"] * Lq * Tr if pol.get("loop") else 1.0
        ideas_m = 1 + p["idea_gain"] * Tr if (pol.get("ideas") and on) else 1.0
        X = I * min(Q * (K / 0.35) ** 0.5 * tools * vis * ideas_m, p["x_cap"])
        # root-cause fixes act on the reducible part of the pool; firefighting clears symptoms
        # on demand (contractors/overtime above the cap) but 80% come back
        fix = p["phi"] * X * max(P - p["p_min"], 0) + p["phi_ff"] * (1 - u) * demand * P * (1 - p["recur"])
        gen = p["gen0"] * C * (1 - p["std_prevent"] * Ld) * (1 + p["unserved_gen"] * u)
        # outcomes
        detect = 1 - p["scope"] * Lq * a * p["loop_eff"] * Tr if pol.get("loop") else 1.0
        cam_scrap = 1 + p["cam_scrap"] * p["scope"] * cam / 0.40 if pol.get("camera") else 1.0
        scrap = P * detect * cam_scrap * (1 + 0.3 * u)
        esc = P ** 0.38 * (1 - p["scope"] * Lq * a * p["esc_eff"] * Tr if pol.get("loop") else 1.0) \
            * (1 - p["scope"] * cam * p["cam_esc"] if pol.get("camera") else 1.0)
        down = P ** 1.36 * (1 - a * p["dt_red"] * Ld / 0.8) * (1 + 0.3 * u)
        nva = 0.20 * P ** 1.24 * (1 - a * p["nva_red"] * Lq)
        energy = 1 - a * p["e_red"] * Ld / 0.8
        months = 8 * C * (1 - a * p["var_red"] * Ld / 0.8)
        # cost index (2023 = 100): labor + energy escalate 4%/yr (Ex.9), others nominal flat
        if nva_2025 is None and t >= 2025.0:
            nva_2025 = nva
        h = (1 - 0.20) / (1 - nva)
        if nva_2025 is not None and nva < nva_2025:      # only half of freed time becomes cash
            h25 = (1 - 0.20) / (1 - nva_2025)
            h = h25 - p["cash_conv"] * (h25 - h)
        esc_f = (1 + FACT["esc"]) ** (t - T0)
        maint = 1 - p["maint_var"] + p["maint_var"] * down
        # constant 2025 prices: labor and energy held at their 2025 escalation, so the
        # index equals the nominal one in 2025 and compares with build_model.py's 96.9
        esc_25 = (1 + FACT["esc"]) ** 2
        real = 100 * (SPLIT["labor"] * h * esc_25 + SPLIT["energy"] * energy * esc_25 + SPLIT["maint"] * maint
                      + SPLIT["dep"] + SPLIT["scrap"] * scrap)
        nominal = 100 * (SPLIT["labor"] * h * esc_f + SPLIT["energy"] * energy * esc_f
                         + SPLIT["maint"] * maint + SPLIT["dep"] + SPLIT["scrap"] * scrap)
        ideas = 1.08 * X / 0.28                           # Ex.6A: 1.08 implemented ideas/engineer in 2023
        spent = (frozen_share if stopped else capex_target(t, pol, phasing)) if pol.get("capex") is not None \
            or pol.get("loop") else 0.0
        for k, v in (("t", t), ("P", P), ("Q", Q), ("K", K), ("S", S), ("Tr", Tr), ("Lq", Lq), ("Ld", Ld),
                     ("R", routine), ("I", I), ("ideas", ideas), ("scrap", scrap), ("esc", esc),
                     ("down", down), ("nva", nva), ("energy", energy), ("months", months),
                     ("cost_idx", nominal), ("cost_idx_real", real), ("u", u), ("spent", spent)):
            out[k][i] = v
        # ---- go/no-go gate at end-2027 (shifted by any delay): scale only on evidence
        if gate and pol.get("loop") and not stopped and abs(t - (s + pol.get("gate_at", 1.25))) < DT / 2:
            pilot_cut = p["loop_eff"] * a * Tr        # in-scope scrap cut measured in the pilot
            if not (pilot_cut >= 0.60 and Tr >= 0.80 and Lq >= 0.15 and ideas >= 0.75):
                stopped, frozen_share = True, capex_target(t, pol, phasing)
        # ---- integrate stocks
        if pol.get("frozen") and t >= 2025.0:
            continue
        dP = gen - fix
        if I < p["i_norm"]:
            dQ = p["erode"] * (I / p["i_norm"] - 1) * (Q - p["q_floor"])
        else:
            dQ = p["build"] * (I / p["i_norm"] - 1) * (p["q_max"] - Q)
        std = p["k_std_gain"] * Lq if pol.get("loop") else 0.0
        spr = p["sprint"] if (pol.get("sprints") and on) else 0.0
        dK = (p["kc"] * (1 + std) * X + spr) * (1 - K) - p["k_decay"] * K
        acad = pol.get("academy") and on
        dL1 = -p["p12"] * L1 if acad else 0.0
        dL2 = (p["p12"] * L1 - p["p23"] * L2) if acad else 0.0
        dL3 = p["p23"] * L2 if acad else 0.0
        target_tr = p["tr0"]
        if pol.get("hc") and on:
            target_tr = p["tr_hc"]
        if pol.get("camera") and on:
            target_tr = p["tr0"] - p["fatigue"] * cam
        dTr = (target_tr - Tr) / p["tr_tau"]
        dLq = dLd = dcam = 0.0
        share = frozen_share if stopped else capex_target(t, pol, phasing)
        if ended:                                      # standards no one maintains decay
            dLq, dLd = -Lq / 2.0, -Ld / 2.0
        elif pol.get("loop") and on:
            cap = p["build_per_eng"] * S + (p["partner_build"] if t < s + 1.25 else 0.0)
            dLq = min(max(share - Lq, 0) / 0.5, cap)
            dLd = min(max(0.8 * share - Ld, 0) / 0.5, cap)
        if pol.get("camera") and on:
            dcam = max(share - cam, 0) / 0.5            # vendor install: not capability-limited
        P = max(P + dP * DT, 0.05)
        Q = float(np.clip(Q + dQ * DT, p["q_floor"], p["q_max"]))
        K = float(np.clip(K + dK * DT, 0, 0.95))
        L1, L2, L3 = L1 + dL1 * DT, L2 + dL2 * DT, L3 + dL3 * DT
        Tr = float(np.clip(Tr + dTr * DT, 0.3, 0.98))
        Lq, Ld, cam = min(Lq + dLq * DT, 1.0), min(Ld + dLd * DT, 0.8), min(cam + dcam * DT, 1.0)
    out["stopped"] = stopped
    return out


def annual(out, key, year):
    """Calendar-year mean of a monthly series."""
    m = (out["t"] >= year) & (out["t"] < year + 1)
    return float(out[key][m].mean())


def at(out, key, year):
    """Value at the start of a year (how the exhibits report 2023 and 2025)."""
    return float(out[key][int(round((year - T0) / DT))])


# ---------------------------------------------------------------- calibration
def calibrate(p):
    """Fit gen0, erode and kc to the 2023 -> 2025 exhibit movements (do-nothing)."""
    p = dict(p)
    p["gen0"], p["erode"], p["kc"] = 0.33, 1.0, 0.13
    for _ in range(8):
        for key, target, sel in (("gen0", 1.08, lambda o: at(o, "P", 2025)),
                                 ("erode", 0.67, lambda o: at(o, "ideas", 2025)),
                                 ("kc", 0.33, lambda o: at(o, "K", 2025))):
            lo, hi = 0.0, (20.0 if key == "erode" else 3.0)
            for _ in range(40):
                mid = (lo + hi) / 2
                p[key] = mid
                v = sel(simulate(p, POLICIES["do_nothing"]))
                increasing = key != "erode"          # higher erode -> fewer ideas
                if (v < target) == increasing:
                    lo = mid
                else:
                    hi = mid
            p[key] = (lo + hi) / 2
    return p


# ---------------------------------------------------------------- economics
def economics(p, pol_key, base_out, out=None, phasing=PHASING, frozen_out=None):
    """Cash flows vs the do-nothing counterfactual and vs a frozen-2025 baseline (Rp B)."""
    pol = POLICIES[pol_key]
    phasing = pol.get("phasing", phasing)
    out = out if out is not None else simulate(p, pol, phasing)
    frozen_out = frozen_out if frozen_out is not None else simulate(p, POLICIES["frozen_2025"])
    capex = pol.get("capex", p["capex"]) if (pol.get("loop") or pol.get("capex")) else 0.0
    training = pol.get("training", p["training"])
    scale = FACT["conv_cost_2025"] / at(base_out, "cost_idx", 2025)
    rows, cum_inv = [], 0.0
    stop_share = out["spent"][-1] if out["stopped"] else None
    for y in range(2026, 2036):
        shift = pol.get("delay", 0.0)
        share = phasing.get(int(round(y - shift)), 0.0) if y - shift == int(y - shift) else 0.0
        if stop_share is not None:
            prev = sum(v for k, v in phasing.items() if k + shift < y)
            share = max(0.0, min(share, stop_share - prev))
        inv = capex * share
        cum_inv += inv
        active = y + 1 > START + shift and capex + training > 0 and y < pol.get("end", 99e9)
        if y > 2030 and active:                 # Ex.9: 5-year technology life -> renew 1/5 a year
            inv = cum_inv / FACT["life"]
        run = (cum_inv * p["run_pct"] + (training if y <= 2030 else training * 0.6)) * active
        conv_dn = annual(base_out, "cost_idx", y) * scale
        conv = annual(out, "cost_idx", y) * scale
        var_dn = p["var_projects"] * p["var_cost"] * annual(base_out, "months", y) / 9
        var = p["var_projects"] * p["var_cost"] * annual(out, "months", y) / 9
        energy_rp = (annual(base_out, "energy", y) - annual(out, "energy", y)) * SPLIT["energy"] \
            * FACT["conv_cost_2025"] * (1 + FACT["esc"]) ** (y - 2025)
        sav = (conv_dn - conv) + (var_dn - var)
        var_fr = p["var_projects"] * p["var_cost"] * annual(frozen_out, "months", y) / 9
        sav_frozen = (annual(frozen_out, "cost_idx", y) - annual(out, "cost_idx", y)) * scale + (var_fr - var)
        rows.append(dict(year=y, inv=inv, run=run, sav=sav, sav_frozen=sav_frozen, energy_rp=energy_rp,
                         net=sav - inv - run, net_frozen=sav_frozen - inv - run))
    win = [r for r in rows if r["year"] <= 2030]
    disc = [(1 + FACT["disc"]) ** -(r["year"] - 2025) for r in win]
    npv = sum(r["net"] * d for r, d in zip(win, disc))
    npv_frozen = sum(r["net_frozen"] * d for r, d in zip(win, disc))
    cum, pb, spent = 0.0, None, False
    for r in win:
        cum += r["net"]
        spent = spent or cum < 0
        if pb is None and spent and cum >= 0:
            pb = r["year"]
    irr = _irr([r["net"] for r in win])
    npv35 = sum(r["net"] * (1 + FACT["disc"]) ** -(r["year"] - 2025) for r in rows)
    npv35_frozen = sum(r["net_frozen"] * (1 + FACT["disc"]) ** -(r["year"] - 2025) for r in rows)
    return dict(rows=rows, npv=npv, npv_frozen=npv_frozen, npv35=npv35, npv35_frozen=npv35_frozen, payback=pb, irr=irr, capex=capex,
                stopped=out["stopped"])


def _irr(flows):
    if not (min(flows) < 0 < max(flows)):
        return None
    lo, hi = -0.99, 10.0
    f = lambda r: sum(c / (1 + r) ** (k + 1) for k, c in enumerate(flows))
    if f(lo) * f(hi) > 0:
        return None
    for _ in range(200):
        mid = (lo + hi) / 2
        if f(lo) * f(mid) <= 0:
            hi = mid
        else:
            lo = mid
    return (lo + hi) / 2


# ---------------------------------------------------------------- sustainability
def sustainability(p, econ, out, base_out):
    """Environmental and social outcomes vs do-nothing."""
    env = []
    for r in econ["rows"]:
        kwh = r["energy_rp"] * 1e9 * p["elec_share"] / p["tariff"]
        t_co2 = kwh / 1000 * p["grid_ef"]
        env.append(dict(year=r["year"], mwh=kwh / 1000, tco2=t_co2, carbon_rp=t_co2 * 1000 * p["carbon_tax"] / 1e9))
    end = lambda key, y: at(out, key, min(y + 1, YEARS[-1]))
    social = {y: dict(digital_l3=end("S", y), know_how=end("K", y),
                      senior_dep=0.48 * (1 - end("K", y)) / 0.67,
                      ramp_months=6 + 9 * (1 - end("K", y)) / 0.67,
                      routine=annual(out, "R", y), improve=annual(out, "I", y),
                      ideas=annual(out, "ideas", y)) for y in (2025, 2030, 2035)}
    return dict(env=env, social=social)


def bench(year, moving=True):
    """New-player index: static at 89, or ILLUSTRATIVE linear trend of -2.5/yr (Ex.3)."""
    return FACT["bench_2025"] - (2.5 * (year - 2025) if moving else 0.0)


# ---------------------------------------------------------------- Monte Carlo
UNCERTAIN = {  # (low, mode, high) triangular
    "cplx_post": (0.0, 0.03125, 0.0625), "build": (0.2, 0.4, 0.6),
    "tools_gain": (0.2, 0.5, 0.8), "vis_gain": (0.2, 0.5, 0.8), "idea_gain": (0.1, 0.25, 0.4),
    "sprint": (0.06, 0.12, 0.18), "k_std_gain": (0.5, 1.5, 2.5), "tr_hc": (0.78, 0.90, 0.95), "scope": (0.30, 0.40, 0.50),
    "dt_red": (0.10, 0.25, 0.40), "nva_red": (0.15, 0.30, 0.45), "cash_conv": (0.30, 0.50, 0.70),
    "e_red": (0.02, 0.05, 0.08), "var_red": (0.20, 0.35, 0.50), "capex": (60, 80, 110),
    "build_per_eng": (0.03, 0.06, 0.09), "unserved_gen": (0.2, 0.5, 1.0),
    "adopt": (0.6, 1.0, 1.0),
}


def monte_carlo(p, n=1500, seed=2026, policy="clk_v2", phasing=PHASING, gate=True, over=None):
    rng = np.random.default_rng(seed)
    ranges = dict(UNCERTAIN, **(over or {}))
    res = []
    for _ in range(n):
        q = dict(p)
        for k, (a, m, b) in ranges.items():
            q[k] = rng.triangular(a, m, b)
        q = calibrate_fast(q)
        base = simulate(q, POLICIES["do_nothing"])
        out = simulate(q, POLICIES[policy], phasing, gate=gate)
        e = economics(q, policy, base, out, phasing)
        res.append((e["npv"], e["npv_frozen"], annual(out, "cost_idx_real", 2030), e["npv35"],
                    annual(out, "ideas", 2030), out["stopped"], at(out, "S", 2031)))
    a = np.array([r[:5] for r in res])
    return dict(npv=a[:, 0], npv_frozen=a[:, 1], idx_real=a[:, 2], npv35=a[:, 3], ideas=a[:, 4],
                stopped=np.array([r[5] for r in res]), digital=np.array([r[6] for r in res]))


def calibrate_fast(q):
    """Every uncertain input acts only after 2025 (asserted in check()), so the
    2023-25 calibration carries over unchanged."""
    return q


def tornado(p, base_npv, policy="clk_v2"):
    rows = []
    for k, (a, m, b) in UNCERTAIN.items():
        vals = []
        for v in (a, b):
            q = calibrate_fast(dict(p, **{k: v}))
            base = simulate(q, POLICIES["do_nothing"])
            vals.append(economics(q, policy, base)["npv"])
        rows.append((k, min(vals), max(vals)))
    return sorted(rows, key=lambda r: -(r[2] - r[1]))


# ---------------------------------------------------------------- checks
def check(p, runs, econ):
    """Calibration and structure must hold, or the model is not fit to quote."""
    dn = runs["do_nothing"]
    fit = {"P/scrap 2025": (at(dn, "P", 2025), 1.08), "ideas 2025": (at(dn, "ideas", 2025), 0.67),
           "know-how 2025": (at(dn, "K", 2025), 0.33), "routine 2025": (at(dn, "R", 2025), 0.65),
           "variant months 2025": (at(dn, "months", 2025), 9.0),
           "NVA 2025": (at(dn, "nva", 2025), 0.22), "downtime 2025": (at(dn, "down", 2025), 1.11)}
    for k, (got, want) in fit.items():
        assert abs(got / want - 1) < 0.03, f"calibration off: {k} {got:.3f} vs {want}"
    idx = at(dn, "cost_idx", 2025)
    assert abs(idx - 106) < 1.5, f"cost index 2025 {idx:.1f} too far from Ex.3's 106"
    # structure: tech-only must raise scrap (own sim), the loop must cut it
    assert annual(runs["tech_only"], "scrap", 2030) > annual(dn, "scrap", 2030) * 0.98
    assert annual(runs["clk_v2"], "scrap", 2030) < annual(dn, "scrap", 2030)
    # the firewall costs something first: worse before better
    assert max(runs["clk_v2"]["u"]) > 0, "protected time should leave some fires unserved at first"
    # Monte Carlo inputs must not move the calibrated history
    for k, (a, m, b) in UNCERTAIN.items():
        q = dict(p, **{k: b})
        assert abs(at(simulate(q, POLICIES["do_nothing"]), "P", 2025) - at(dn, "P", 2025)) < 1e-9, k
    return fit, idx


# ---------------------------------------------------------------- charts
def charts(runs, mcs, sust):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    ink, ink2, grid = "#0b0b0b", "#52514e", "#e4e3df"
    col = {"do_nothing": "#8a8984", "tech_only": "#eb6834", "people_only": "#1baf7a",
           "clk_v2": "#2a78d6", "clk_v1": "#4a3aa7", "clk_v2_relapse": "#e87ba4"}
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10, "axes.edgecolor": grid,
                         "axes.labelcolor": ink2, "xtick.color": ink2, "ytick.color": ink2,
                         "axes.spines.top": False, "axes.spines.right": False})
    out_dir = HERE.parent / "outputs" / "charts"

    def line_fig(key, title, ylab, keys, fname, scale=1.0, until=2035, ref=None, pct=False):
        fig, ax = plt.subplots(figsize=(7.2, 4.0), dpi=200)
        for k in keys:
            o = runs[k]
            m = o["t"] <= until + 1
            ax.plot(o["t"][m], o[key][m] * scale, color=col[k], lw=2, label=POLICIES[k]["label"])
            last = o[key][m][-1] * scale
            ax.annotate(f"{last:.0%}" if pct else (f"{last:.0f}" if last > 5 else f"{last:.2f}"),
                        (o["t"][m][-1], o[key][m][-1] * scale), xytext=(4, 0), textcoords="offset points",
                        color=ink2, fontsize=8, va="center")
        if ref:
            for y, lab in ref:
                ax.axhline(y, color=ink2, lw=1, ls=(0, (4, 3)))
                ax.text(2023.1, y, lab, color=ink2, fontsize=8, va="bottom")
        ax.axvspan(2026.75, 2031, color="#f0efec", zorder=0)
        ax.text(2026.85, ax.get_ylim()[1], "periode program", color=ink2, fontsize=8, va="top")
        ax.set_title(title, loc="left", color=ink, fontsize=11, fontweight="bold")
        ax.set_ylabel(ylab)
        ax.grid(axis="y", color=grid, lw=0.8)
        ax.legend(frameon=False, fontsize=8, loc="best")
        fig.tight_layout()
        fig.savefig(out_dir / fname)
        plt.close(fig)

    main = ["do_nothing", "tech_only", "people_only", "clk_v2"]
    line_fig("cost_idx_real", "Indeks biaya konversi pada harga 2025: hanya CLK v2 yang terus turun",
             "indeks biaya, harga konstan 2025 (skala Ex.3: 2025 = 106)", main, "fig_sd_cost.png")
    line_fig("scrap", "Indeks scrap: kamera saja menaikkan scrap, loop tertutup memangkasnya",
             "indeks (2023 = 1)", main, "fig_sd_scrap.png")
    line_fig("I", "Waktu engineer untuk perbaikan (beli teknologi = tanpa tindakan)",
             "porsi waktu", ["do_nothing", "people_only", "clk_v2"], "fig_sd_time.png",
             ref=[(0.30, "norma 30%")], pct=True)
    line_fig("cost_idx_real", "Bila program dihentikan 2031, biaya naik lagi",
             "indeks biaya, harga konstan 2025 (skala Ex.3: 2025 = 106)", ["do_nothing", "clk_v2", "clk_v2_relapse"],
             "fig_sd_durability.png")
    # Monte Carlo: P5-P95 range and median per strategy (one axis, one unit)
    ID = {"CLK v2, pilot-light + gate": "Rencana: pilot-light + gate",
          "CLK v2, pilot-light, no gate": "Pilot-light tanpa gate",
          "CLK v2, front-loaded + gate": "Belanja di awal + gate",
          "CLK v2, front-loaded, no gate": "Belanja di awal tanpa gate",
          "FAILURE (adoption 20-60%): pilot-light + gate": "Loop gagal: pilot-light + gate",
          "FAILURE (adoption 20-60%): front-loaded + gate": "Loop gagal: belanja di awal + gate",
          "CLK v1 (no protected time) + gate": "Tanpa perlindungan waktu (v1)",
          "CLK v2 protecting 40% + gate": "Lindungi 40% waktu",
          "CLK v2, 1 year late + gate": "Rencana, terlambat 1 tahun"}
    rows = [(ID[lab], m) for lab, m in mcs.items() if lab in ID]
    fig, ax = plt.subplots(figsize=(8.4, 0.48 * len(rows) + 1.3), dpi=200)
    for i, (lab, mm) in enumerate(reversed(rows)):
        lo, mid, hi = np.percentile(mm["npv"], [5, 50, 95])
        c = col["clk_v2"] if lab.startswith("Rencana:") else ink2
        ax.plot([lo, hi], [i, i], color=c, lw=2, solid_capstyle="round")
        ax.plot([mid], [i], "o", color=c, ms=7, mec="white", mew=1.5)
        ax.text(hi + 1.5, i, f"P(NPV>0) {(mm['npv'] > 0).mean():.0%}", va="center", fontsize=8, color=ink2)
    ax.set_yticks(range(len(rows)))
    ax.set_yticklabels([lab for lab, _ in reversed(rows)], fontsize=8, color=ink)
    ax.axvline(0, color=ink, lw=1)
    ax.set_xlabel("NPV 2026-2030, Rp miliar (garis P5-P95, titik median)")
    ax.set_title("NPV per strategi, 1.500 simulasi", loc="left",
                 color=ink, fontsize=11, fontweight="bold")
    ax.grid(axis="x", color=grid, lw=0.8)
    ax.set_xlim(right=ax.get_xlim()[1] + 18)
    fig.tight_layout()
    fig.savefig(out_dir / "fig_sd_mc.png")
    plt.close(fig)
    # CO2 avoided per year (single series, bars)
    fig, ax = plt.subplots(figsize=(7.2, 3.6), dpi=200)
    yrs = [e["year"] for e in sust["env"]]
    vals = [e["tco2"] for e in sust["env"]]
    ax.bar(yrs, vals, color=col["clk_v2"], width=0.6)
    for x, v in zip(yrs, vals):
        if x in (2027, 2030, 2035):
            ax.text(x, v, f"{v:,.0f}".replace(",", "."), ha="center", va="bottom", fontsize=8, color=ink2)
    ax.set_title("Emisi CO2 yang dihindari dari loop energi (ton/tahun)", loc="left", color=ink,
                 fontsize=11, fontweight="bold")
    ax.grid(axis="y", color=grid, lw=0.8)
    fig.tight_layout()
    fig.savefig(out_dir / "fig_sd_co2.png")
    plt.close(fig)


# ---------------------------------------------------------------- main
def main(quick=False):
    p = calibrate(BASE)
    print("== Calibrated parameters (do-nothing must reproduce Ex.4/6A 2023 -> 2025)")
    print(f"  gen0 {p['gen0']:.4f}  erode {p['erode']:.4f}  kc {p['kc']:.4f}")
    runs = {k: simulate(p, pol) for k, pol in POLICIES.items()}
    base = runs["do_nothing"]
    econ = {k: economics(p, k, base, runs[k], frozen_out=runs["frozen_2025"])
            for k in POLICIES if k not in ("do_nothing", "frozen_2025")}
    fit, idx25 = check(p, runs, econ)
    print("\n== Calibration fit (model vs exhibit)")
    for k, (got, want) in fit.items():
        print(f"  {k:<22} {got:7.3f} vs {want}")
    print(f"  cost index 2025        {idx25:7.1f} vs 106 (Ex.3)")
    print(f"  cost index 2024        {at(base, 'cost_idx', 2024):7.1f} vs 103 (Ex.3)")

    print("\n== Scenarios: operational outcomes 2030 (calendar-year mean)")
    hdr = ("Policy", "cost idx", "at 2025 Rp", "scrap", "escape", "downtime", "NVA", "var mo", "improve", "ideas",
           "know-how", "L3+ SW&AI")
    print("  " + " | ".join(f"{h:>10}" for h in hdr))
    summary = {}
    for k, o in runs.items():
        row = dict(cost=annual(o, "cost_idx", 2030), real=annual(o, "cost_idx_real", 2030),
                   scrap=annual(o, "scrap", 2030) * 100, esc=annual(o, "esc", 2030) * 100,
                   down=annual(o, "down", 2030) * 100, nva=annual(o, "nva", 2030), months=annual(o, "months", 2030),
                   improve=annual(o, "I", 2030), ideas=annual(o, "ideas", 2030), K=at(o, "K", 2031),
                   S=at(o, "S", 2031), real2035=annual(o, "cost_idx_real", 2035), cost2035=annual(o, "cost_idx", 2035),
                   tr=at(o, "Tr", 2031), stopped=o["stopped"])
        summary[k] = row
        print(f"  {POLICIES[k]['label'][:22]:>22} | " + " | ".join(
            f"{row[c]:10.1f}" if c not in ("nva", "improve", "K") else f"{row[c]:10.0%}"
            for c in ("cost", "real", "scrap", "esc", "down", "nva", "months", "improve", "ideas", "K", "S")))

    print("\n== Worse before better: CLK v2 vs do-nothing, scrap and cost (at 2025 prices)")
    for y in (2026.75, 2027.0, 2027.5, 2028.0, 2029.0, 2030.0):
        print(f"  t={y:7.2f}  scrap {at(runs['clk_v2'], 'scrap', y):.3f} vs {at(base, 'scrap', y):.3f}  "
              f"unserved fires {at(runs['clk_v2'], 'u', y):.1%}  capability Q {at(runs['clk_v2'], 'Q', y):.2f}")

    print("\n== Economics (Rp B, 2026-2030, 10%): savings vs do-nothing counterfactual | vs frozen 2025")
    for k, e in econ.items():
        pb = e["payback"] or "after 2030"
        irr = f"{e['irr']:.0%}" if e["irr"] is not None else "n/a"
        print(f"  {POLICIES[k]['label'][:34]:<34} capex {e['capex']:5.0f}  NPV {e['npv']:7.1f} | {e['npv_frozen']:7.1f}"
              f"  NPV 2026-35 incl. renewal {e['npv35']:7.1f} | {e['npv35_frozen']:7.1f}"
              f"  payback {pb}  IRR {irr}  gate stopped: {e['stopped']}")
    e = econ["clk_v2"]
    print("  CLK v2 by year: " + "  ".join(f"{r['year']}: sav {r['sav']:.1f} inv {r['inv']:.1f} run {r['run']:.1f}"
                                          for r in e["rows"][:5]))
    run_rate = e["rows"][4]["sav"]
    print(f"  CLK v2 savings 2030 {run_rate:.1f} = {run_rate / (FACT['conv_cost_2025'] * 1.04 ** 5):.1%} "
          f"of 2030 conversion cost")

    print("\n== Competitive gap (index points; benchmark static 89 | ILLUSTRATIVE moving -2.5/yr)")
    for k in ("do_nothing", "tech_only", "people_only", "clk_v2"):
        c = summary[k]["cost"]
        print(f"  {POLICIES[k]['label'][:24]:<24} 2030 nominal {c:6.1f}  gap static {c - bench(2030, False):5.1f}"
              f"  gap moving {c - bench(2030):5.1f}")
    dn_gap = summary["do_nothing"]["cost"] - bench(2030)
    v2_gap = summary["clk_v2"]["cost"] - bench(2030)
    print(f"  Share of the 2030 do-nothing gap (moving benchmark) that CLK v2 removes: "
          f"{(dn_gap - v2_gap) / dn_gap:.0%}")
    prog_dep = 80 / FACT["life"] / (FACT["conv_cost_2025"] / 106)
    print(f"  Program capex depreciation if charged to the index: +{prog_dep:.1f} pts/yr during its 5-yr life")

    sust = sustainability(p, e, runs["clk_v2"], base)
    print("\n== Sustainability (CLK v2 vs do-nothing)")
    env = {r["year"]: r for r in sust["env"]}
    tot = sum(r["tco2"] for r in sust["env"] if r["year"] <= 2030)
    tot35 = sum(r["tco2"] for r in sust["env"])
    print(f"  Environmental: energy saved 2030 {env[2030]['mwh']:,.0f} MWh/yr, CO2 avoided {env[2030]['tco2']:,.0f} t/yr; "
          f"cumulative {tot:,.0f} t (2026-30), {tot35:,.0f} t (2026-35); carbon-tax value 2030 Rp{env[2030]['carbon_rp']:.2f} B")
    print(f"  Scrap (material waste) index 2030: {summary['clk_v2']['scrap']:.0f} vs do-nothing "
          f"{summary['do_nothing']['scrap']:.0f} ({summary['clk_v2']['scrap'] / summary['do_nothing']['scrap'] - 1:+.0%})")
    for y, s in sust["social"].items():
        print(f"  Social {y}: SW&AI L3+ {s['digital_l3']:.1f}/30, know-how {s['know_how']:.0%}, "
              f"processes on 1-2 seniors {s['senior_dep']:.0%}, new engineer independent {s['ramp_months']:.1f} mo, "
              f"routine {s['routine']:.0%}, improvement {s['improve']:.0%}, ideas/eng {s['ideas']:.2f}")
    sdn = sustainability(p, e, base, base)["social"][2030]
    print(f"  Social 2030 do-nothing: know-how {sdn['know_how']:.0%}, seniors {sdn['senior_dep']:.0%}, "
          f"routine {sdn['routine']:.0%}, ideas/eng {sdn['ideas']:.2f}")
    print(f"  Durability 2035 (at 2025 prices): CLK v2 {summary['clk_v2']['real2035']:.1f}, relapse "
          f"{summary['clk_v2_relapse']['real2035']:.1f}, tech-only {summary['tech_only']['real2035']:.1f}, "
          f"do-nothing {summary['do_nothing']['real2035']:.1f}")

    results = dict(params={k: (float(v) if isinstance(v, (int, float, np.floating)) else v) for k, v in p.items()},
                   summary=summary, econ={k: {kk: vv for kk, vv in v.items() if kk != "rows"} for k, v in econ.items()},
                   clk_v2_rows=e["rows"], env=sust["env"], social=sust["social"])
    if not quick:
        print(f"\n== Monte Carlo (1,500 runs each, {len(UNCERTAIN)} uncertain inputs, triangular)")
        mc = monte_carlo(p)
        mc_v1 = monte_carlo(p, policy="clk_v1")
        mc_ng = monte_carlo(p, gate=False)
        mc_fr = monte_carlo(p, phasing=FRONT, gate=False)
        mc_late = monte_carlo(p, policy="clk_v2_late")
        mc_hard = monte_carlo(p, policy="clk_v2_hard")
        mc_tech = monte_carlo(p, policy="tech_only", gate=False)
        mc_frg = monte_carlo(p, policy="clk_v2_front")
        fail = {"adopt": (0.2, 0.4, 0.6)}   # outside both models' 60% adoption floor: the loop mostly fails
        mc_fail = monte_carlo(p, n=800, over=fail)
        mc_fail_fr = monte_carlo(p, n=800, policy="clk_v2_front", over=fail)
        mcs = {"CLK v2, pilot-light + gate": mc, "CLK v2, pilot-light, no gate": mc_ng,
               "CLK v2, front-loaded + gate": mc_frg, "CLK v2, front-loaded, no gate": mc_fr,
               "FAILURE (adoption 20-60%): pilot-light + gate": mc_fail,
               "FAILURE (adoption 20-60%): front-loaded + gate": mc_fail_fr, "CLK v1 (no protected time) + gate": mc_v1,
               "CLK v2 protecting 40% + gate": mc_hard, "CLK v2, 1 year late + gate": mc_late,
               "Buy technology only": mc_tech}
        results["mc"] = {}
        for lab, m in mcs.items():
            r = dict(p_pos=float((m["npv"] > 0).mean()), p5=float(np.percentile(m["npv"], 5)),
                     p50=float(np.median(m["npv"])), p95=float(np.percentile(m["npv"], 95)),
                     p_pos_frozen=float((m["npv_frozen"] > 0).mean()), gate_stop=float(m["stopped"].mean()),
                     idx_real_p50=float(np.median(m["idx_real"])), digital_p50=float(np.median(m["digital"])),
                     p_pos35=float((m["npv35"] > 0).mean()), npv35_p50=float(np.median(m["npv35"])),
                     ideas_p50=float(np.median(m["ideas"])), p_ideas_target=float((m["ideas"] >= 2.4).mean()))
            results["mc"][lab] = r
            print(f"  {lab:<46} P(NPV>0) {r['p_pos']:.0%} (frozen-2025 {r['p_pos_frozen']:.0%})  "
                  f"P5 {r['p5']:6.1f}  P50 {r['p50']:6.1f}  P95 {r['p95']:6.1f}  gate stop {r['gate_stop']:.0%}  "
                  f"| 2026-35: P(NPV>0) {r['p_pos35']:.0%} P50 {r['npv35_p50']:6.1f} | ideas 2030 P50 {r['ideas_p50']:.1f}, "
                  f"P(>=2.4) {r['p_ideas_target']:.0%}")
        print("\n== Tornado (NPV, CLK v2, one input at a time at its low/high)")
        tor = tornado(p, e["npv"])
        for k, lo, hi in tor[:8]:
            print(f"  {k:<14} {lo:6.1f} .. {hi:6.1f}")
        results["tornado"] = tor
        charts(runs, mcs, sust)
        print("\n  charts saved to outputs/charts/fig_sd_*.png")
    (HERE / "sd_results.json").write_text(json.dumps(results, indent=1, default=float))
    print("\nall checks passed; results in model/sd_results.json")


if __name__ == "__main__":
    main(quick="--quick" in sys.argv)
