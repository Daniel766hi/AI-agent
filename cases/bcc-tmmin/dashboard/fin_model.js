// JavaScript port of the spreadsheet financial model (model/build_model.py, Model tab),
// so the dashboard can recompute NPV as levers move. check_parity.js asserts it matches
// model/run_tests.py (base NPV, run-rate) and the documented scenario NPVs.
(function (root) {
  const BASE = {
    units: 175000, unitCost: 3.2, disc: 0.10, esc: 0.04, life: 5, idx2025: 106, bench2025: 89,
    split: { labor: 0.40, energy: 0.12, maint: 0.13, dep: 0.25, scrap: 0.10 },
    nva: 0.22, months: 9, varProjects: 3, varCost: 10, cashConv: 0.50,
    ramp: [0.10, 0.35, 0.65, 0.90, 1.00],
  };
  const PHASING = { light: [0.10, 0.15, 0.40, 0.25, 0.10], front: [0.30, 0.35, 0.25, 0.10, 0.0] };
  const SCEN = {
    konservatif: { scrap: 0.20, maint: 0.05, nvaCut: 0.15, energy: 0.02, variant: 0.20, capex: 110, runPct: 0.10, training: 3.0 },
    dasar: { scrap: 0.35, maint: 0.10, nvaCut: 0.30, energy: 0.05, variant: 0.35, capex: 80, runPct: 0.10, training: 2.5 },
    optimis: { scrap: 0.50, maint: 0.15, nvaCut: 0.45, energy: 0.08, variant: 0.50, capex: 60, runPct: 0.08, training: 2.0 },
  };

  function irr(flows) {
    if (!(Math.min(...flows) < 0 && Math.max(...flows) > 0)) return null;
    const f = (r) => flows.reduce((a, c, k) => a + c / Math.pow(1 + r, k + 1), 0);
    let lo = -0.99, hi = 10;
    if (f(lo) * f(hi) > 0) return null;
    for (let i = 0; i < 200; i++) { const m = (lo + hi) / 2; if (f(lo) * f(m) <= 0) hi = m; else lo = m; }
    return (lo + hi) / 2;
  }

  // lv: { scrap, maint, nvaCut, energy, variant, capex, runPct, training, phasing, laborShare, cashConv, delay }
  function run(lv) {
    const b = BASE;
    const conv = b.units * b.unitCost / 1000;                 // Rp B (Ex.9: ~560)
    const labor = lv.laborShare ?? b.split.labor;
    const cash = lv.cashConv ?? b.cashConv;
    const phasing = PHASING[lv.phasing || "light"];
    const delay = lv.delay || 0;                              // savings ramp shifted later, spend unchanged
    const ramp = b.ramp.map((_, i) => (i - delay >= 0 ? b.ramp[i - delay] : 0));
    const lever = {
      scrap: conv * b.split.scrap * lv.scrap,
      maint: conv * b.split.maint * lv.maint,
      labor: conv * labor * b.nva * lv.nvaCut * cash,
      energy: conv * b.split.energy * lv.energy,
      variant: b.varProjects * b.varCost * lv.variant,
    };
    const runRate = Object.values(lever).reduce((a, v) => a + v, 0);
    const rows = [];
    let cumInv = 0, cum = 0, payback = null;
    for (let i = 0; i < 5; i++) {
      const escF = Math.pow(1 + b.esc, i);
      const by = Object.fromEntries(Object.entries(lever).map(([k, v]) => [k, v * ramp[i] * escF]));
      const sav = Object.values(by).reduce((a, v) => a + v, 0);
      const inv = lv.capex * phasing[i];
      cumInv += inv;
      const runC = cumInv * lv.runPct + lv.training;
      const net = sav - inv - runC;
      const pv = net / Math.pow(1 + b.disc, i + 1);
      cum += net;
      if (payback === null && cum >= 0) payback = 2026 + i;
      rows.push({ year: 2026 + i, ...by, sav, inv, run: runC, net, pv, cum });
    }
    const npv = rows.reduce((a, r) => a + r.pv, 0);
    const idx = b.idx2025 * (1 - runRate / conv);
    const gapClosed = (b.idx2025 - idx) / (b.idx2025 - b.bench2025);
    const residual = rows.reduce((a, r, i) => a + r.inv * ((i + 1 - 0.5) / b.life), 0) / Math.pow(1 + b.disc, b.life);
    return { conv, lever, runRate, rows, npv, npvResidual: npv + residual, irr: irr(rows.map((r) => r.net)), payback,
      idx, gapClosed, months: b.months * (1 - lv.variant) };
  }

  function breakEven(invest) {
    const b = BASE, conv = b.units * b.unitCost / 1000;
    let pvf = 0;
    for (let t = 1; t <= 5; t++) pvf += Math.pow(1 + b.esc, t - 1) / Math.pow(1 + b.disc, t);
    const gapRp = (b.idx2025 - b.bench2025) / b.idx2025 * conv;
    const first = invest / pvf;
    return { pvf, first, pctConv: first / conv, shareGap: first / gapRp, gapRp };
  }

  root.FinModel = { run, breakEven, SCEN, PHASING, BASE };
  if (typeof module !== "undefined") module.exports = root.FinModel;
})(typeof window !== "undefined" ? window : globalThis);
