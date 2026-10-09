// JavaScript port of model/sd_model.py (simulate + economics + sustainability),
// so the dashboard can re-run the system dynamics model in the browser.
// check_parity.js asserts it reproduces model/sd_results.json; keep the two in step.
(function (root) {
  const DT = 1 / 12, T0 = 2023.0, T_END = 2036.0;
  const STEPS = Math.round((T_END - T0) / DT);
  const YEARS = Array.from({ length: 13 }, (_, i) => 2023 + i);
  const FACT = { conv: 560.0, disc: 0.10, esc: 0.04, life: 5 };
  const SPLIT = { labor: 0.40, energy: 0.12, maint: 0.13, dep: 0.25, scrap: 0.10 };
  const START = 2026.75;
  const PHASING = { 2026: 0.10, 2027: 0.15, 2028: 0.40, 2029: 0.25, 2030: 0.10 };
  const FRONT = { 2026: 0.30, 2027: 0.35, 2028: 0.25, 2029: 0.10, 2030: 0.0 };
  const POLICIES = {
    do_nothing: { label: "Tanpa tindakan" },
    frozen_2025: { label: "Kinerja dibekukan di 2025", frozen: true },
    tech_only: { label: "Beli teknologi saja", camera: true, capex: 80.0, training: 0.5 },
    people_only: { label: "Program SDM saja", academy: true, ideas: true, firewall: true, ratchet: true, sprints: true, capex: 12.0, training: 3.0 },
    clk_v1: { label: "Closed-Loop Kaizen v1", loop: true, academy: true, ideas: true, sprints: true, hc: true },
    clk_v2: { label: "Closed-Loop Kaizen v2", loop: true, academy: true, ideas: true, sprints: true, hc: true, firewall: true, ratchet: true },
  };
  const clip = (x, a, b) => Math.min(Math.max(x, a), b);
  const has = (o, k) => Object.prototype.hasOwnProperty.call(o, k) && o[k] !== undefined;

  function firewallLevel(t, pol) {
    const s = START + (pol.delay || 0);
    if (!pol.firewall || t < s || t >= (has(pol, "end") ? pol.end : 99e9)) return 0;
    return (has(pol, "protect") ? pol.protect : 0.30) * Math.min(1, (t - s) / 0.5);
  }
  function capexTarget(t, pol, phasing) {
    const shift = pol.delay || 0;
    let cum = 0;
    for (const [y, sh] of Object.entries(phasing)) {
      const y0 = +y + shift;
      if (t >= y0 + 1) cum += sh; else if (t > y0) cum += sh * (t - y0);
    }
    return cum;
  }

  function simulate(p, pol, phasingIn, gate = true) {
    const phasing = pol.phasing || phasingIn || PHASING;
    const n = STEPS;
    const keys = ["t", "P", "Q", "K", "S", "Tr", "Lq", "Ld", "R", "I", "ideas", "scrap", "esc", "down", "nva",
      "energy", "months", "cost_idx", "cost_idx_real", "u", "spent"];
    const out = Object.fromEntries(keys.map((k) => [k, new Float64Array(n)]));
    let P = 1.0, Q = 1.0, K = 0.35, Tr = p.tr0, Lq = 0, Ld = 0;
    let L1 = 20.0, L2 = 8.0, L3 = 2.0;
    const s = START + (pol.delay || 0);
    const end = has(pol, "end") ? pol.end : 99e9;
    let stopped = false, frozenShare = null, cam = 0, nva2025 = null, ratchetHi = 0, gateTime = null;
    const gateAt = s + (has(pol, "gate_at") ? pol.gate_at : 1.25);
    for (let i = 0; i < n; i++) {
      const t = T0 + i * DT;
      const on = s <= t && t < end;
      const ended = t >= end;
      const C = 1 + p.cplx_pre * Math.min(t - T0, 2.0) + p.cplx_post * Math.max(t - 2025.0, 0);
      const S = L3;
      const tools = 1 + p.tools_gain * clip((S - 2) / 12, 0, 1.2);
      let routine = p.r0 * Math.pow(P, p.r_exp) * (1 - p.k_routine * (K - 0.35)) * (1 - p.tool_routine * clip((S - 2) / 12, 0, 1));
      const demand = Math.max(routine, p.r_floor);
      routine = clip(routine, p.r_floor, p.r_cap);
      const natural = 1 - p.other - routine;
      const prot = Math.max(firewallLevel(t, pol), (pol.ratchet && on) ? ratchetHi : 0);
      const I = Math.max(natural, prot);
      if (pol.ratchet && on) ratchetHi = Math.min(Math.max(ratchetHi, natural), 1 - p.other - p.r_floor);
      const u = Math.max(0, I - natural) / routine;
      const a = p.adopt;
      const vis = pol.loop ? 1 + a * p.vis_gain * Lq * Tr : 1;
      const ideasM = (pol.ideas && on) ? 1 + p.idea_gain * Tr : 1;
      const X = I * Math.min(Q * Math.pow(K / 0.35, 0.5) * tools * vis * ideasM, p.x_cap);
      const fix = p.phi * X * Math.max(P - p.p_min, 0) + p.phi_ff * (1 - u) * demand * P * (1 - p.recur);
      const gen = p.gen0 * C * (1 - p.std_prevent * Ld) * (1 + p.unserved_gen * u);
      const detect = pol.loop ? 1 - p.scope * Lq * a * p.loop_eff * Tr : 1;
      const camScrap = pol.camera ? 1 + p.cam_scrap * p.scope * cam / 0.40 : 1;
      const scrap = P * detect * camScrap * (1 + 0.3 * u);
      const esc = Math.pow(P, 0.38) * (pol.loop ? 1 - p.scope * Lq * a * p.esc_eff * Tr : 1)
        * (pol.camera ? 1 - p.scope * cam * p.cam_esc : 1);
      const down = Math.pow(P, 1.36) * (1 - a * p.dt_red * Ld / 0.8) * (1 + 0.3 * u);
      const nva = 0.20 * Math.pow(P, 1.24) * (1 - a * p.nva_red * Lq);
      const energy = 1 - a * p.e_red * Ld / 0.8;
      const months = 8 * C * (1 - a * p.var_red * Ld / 0.8);
      if (nva2025 === null && t >= 2025.0) nva2025 = nva;
      let h = (1 - 0.20) / (1 - nva);
      if (nva2025 !== null && nva < nva2025) {
        const h25 = (1 - 0.20) / (1 - nva2025);
        h = h25 - p.cash_conv * (h25 - h);
      }
      const escF = Math.pow(1 + FACT.esc, t - T0);
      const maint = 1 - p.maint_var + p.maint_var * down;
      const esc25 = Math.pow(1 + FACT.esc, 2);
      const real = 100 * (SPLIT.labor * h * esc25 + SPLIT.energy * energy * esc25 + SPLIT.maint * maint + SPLIT.dep + SPLIT.scrap * scrap);
      const nominal = 100 * (SPLIT.labor * h * escF + SPLIT.energy * energy * escF + SPLIT.maint * maint + SPLIT.dep + SPLIT.scrap * scrap);
      const ideas = 1.08 * X / 0.28;
      const spent = (has(pol, "capex") || pol.loop) ? (stopped ? frozenShare : capexTarget(t, pol, phasing)) : 0;
      const vals = { t, P, Q, K, S, Tr, Lq, Ld, R: routine, I, ideas, scrap, esc, down, nva, energy, months,
        cost_idx: nominal, cost_idx_real: real, u, spent };
      for (const k of keys) out[k][i] = vals[k];
      if (gate && pol.loop && !stopped && Math.abs(t - gateAt) < DT / 2) {
        const pilotCut = p.loop_eff * a * Tr;
        gateTime = { t, pilotCut, Tr, Lq, ideas };
        if (!(pilotCut >= 0.60 && Tr >= 0.80 && Lq >= 0.15 && ideas >= 0.75)) {
          stopped = true; frozenShare = capexTarget(t, pol, phasing);
        }
      }
      if (pol.frozen && t >= 2025.0) continue;
      const dP = gen - fix;
      const dQ = I < p.i_norm ? p.erode * (I / p.i_norm - 1) * (Q - p.q_floor) : p.build * (I / p.i_norm - 1) * (p.q_max - Q);
      const std = pol.loop ? p.k_std_gain * Lq : 0;
      const spr = (pol.sprints && on) ? p.sprint : 0;
      const dK = (p.kc * (1 + std) * X + spr) * (1 - K) - p.k_decay * K;
      const acad = pol.academy && on;
      const dL1 = acad ? -p.p12 * L1 : 0;
      const dL2 = acad ? p.p12 * L1 - p.p23 * L2 : 0;
      const dL3 = acad ? p.p23 * L2 : 0;
      let targetTr = p.tr0;
      if (pol.hc && on) targetTr = p.tr_hc;
      if (pol.camera && on) targetTr = p.tr0 - p.fatigue * cam;
      const dTr = (targetTr - Tr) / p.tr_tau;
      let dLq = 0, dLd = 0, dcam = 0;
      const share = stopped ? frozenShare : capexTarget(t, pol, phasing);
      if (ended) { dLq = -Lq / 2; dLd = -Ld / 2; }
      else if (pol.loop && on) {
        const cap = p.build_per_eng * S + (t < s + 1.25 ? p.partner_build : 0);
        dLq = Math.min(Math.max(share - Lq, 0) / 0.5, cap);
        dLd = Math.min(Math.max(0.8 * share - Ld, 0) / 0.5, cap);
      }
      if (pol.camera && on) dcam = Math.max(share - cam, 0) / 0.5;
      P = Math.max(P + dP * DT, 0.05);
      Q = clip(Q + dQ * DT, p.q_floor, p.q_max);
      K = clip(K + dK * DT, 0, 0.95);
      L1 += dL1 * DT; L2 += dL2 * DT; L3 += dL3 * DT;
      Tr = clip(Tr + dTr * DT, 0.3, 0.98);
      Lq = Math.min(Lq + dLq * DT, 1.0); Ld = Math.min(Ld + dLd * DT, 0.8); cam = Math.min(cam + dcam * DT, 1.0);
    }
    out.stopped = stopped;
    out.gate = gateTime;
    return out;
  }

  function annual(out, key, year) {
    let s = 0, c = 0;
    for (let i = 0; i < out.t.length; i++) if (out.t[i] >= year && out.t[i] < year + 1) { s += out[key][i]; c++; }
    return s / c;
  }
  function at(out, key, year) { return out[key][Math.round((year - T0) / DT)]; }

  function economics(p, pol, baseOut, out, frozenOut, phasingIn) {
    const phasing = pol.phasing || phasingIn || PHASING;
    const capex = (pol.loop || has(pol, "capex")) ? (has(pol, "capex") ? pol.capex : p.capex) : 0;
    const training = has(pol, "training") ? pol.training : p.training;
    const scale = FACT.conv / at(baseOut, "cost_idx", 2025);
    const shift = pol.delay || 0;
    const end = has(pol, "end") ? pol.end : 99e9;
    const stopShare = out.stopped ? out.spent[out.spent.length - 1] : null;
    const rows = [];
    let cumInv = 0;
    for (let y = 2026; y < 2036; y++) {
      let share = Number.isInteger(y - shift) ? (phasing[y - shift] || 0) : 0;
      if (stopShare !== null) {
        let prev = 0;
        for (const [k, v] of Object.entries(phasing)) if (+k + shift < y) prev += v;
        share = Math.max(0, Math.min(share, stopShare - prev));
      }
      let inv = capex * share;
      cumInv += inv;
      const active = (y + 1 > START + shift) && (capex + training > 0) && (y < end);
      if (y > 2030 && active) inv = cumInv / FACT.life;
      const run = (cumInv * p.run_pct + (y <= 2030 ? training : training * 0.6)) * (active ? 1 : 0);
      const convDn = annual(baseOut, "cost_idx", y) * scale, conv = annual(out, "cost_idx", y) * scale;
      const varDn = p.var_projects * p.var_cost * annual(baseOut, "months", y) / 9;
      const v = p.var_projects * p.var_cost * annual(out, "months", y) / 9;
      const energyRp = (annual(baseOut, "energy", y) - annual(out, "energy", y)) * SPLIT.energy * FACT.conv * Math.pow(1 + FACT.esc, y - 2025);
      const sav = (convDn - conv) + (varDn - v);
      const varFr = p.var_projects * p.var_cost * annual(frozenOut, "months", y) / 9;
      const savFrozen = (annual(frozenOut, "cost_idx", y) - annual(out, "cost_idx", y)) * scale + (varFr - v);
      rows.push({ year: y, inv, run, sav, savFrozen, energyRp, net: sav - inv - run, netFrozen: savFrozen - inv - run });
    }
    const df = (y) => Math.pow(1 + FACT.disc, -(y - 2025));
    const win = rows.filter((r) => r.year <= 2030);
    const npv = win.reduce((a, r) => a + r.net * df(r.year), 0);
    const npvFrozen = win.reduce((a, r) => a + r.netFrozen * df(r.year), 0);
    const npv35 = rows.reduce((a, r) => a + r.net * df(r.year), 0);
    let cum = 0, payback = null, spent = false;
    for (const r of win) { cum += r.net; spent = spent || cum < 0; if (payback === null && spent && cum >= 0) payback = r.year; }
    const tco2 = rows.map((r) => ({ year: r.year, tco2: r.energyRp * 1e9 * p.elec_share / p.tariff / 1000 * p.grid_ef }));
    return { rows, npv, npvFrozen, npv35, payback, capex, stopped: out.stopped, tco2 };
  }

  root.SDModel = { simulate, economics, annual, at, POLICIES, PHASING, FRONT, YEARS, START };
  if (typeof module !== "undefined") module.exports = root.SDModel;
})(typeof window !== "undefined" ? window : globalThis);
