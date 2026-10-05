// The browser model must reproduce the Python model, or the dashboard is showing
// something nobody tested. Run: node dashboard/check_parity.js
const path = require("path");
const fs = require("fs");
const M = require("./sd_model.js");
const R = JSON.parse(fs.readFileSync(path.join(__dirname, "..", "model", "sd_results.json"), "utf8"));
const p = R.params;
const base = M.simulate(p, M.POLICIES.do_nothing);
const frozen = M.simulate(p, M.POLICIES.frozen_2025);
let fails = 0;
const close = (label, got, want, tol = 0.05) => {
  const ok = Math.abs(got - want) <= tol;
  if (!ok) fails++;
  console.log(`  ${ok ? "ok  " : "FAIL"}  ${label.padEnd(44)} js ${got.toFixed(3)}  py ${want.toFixed(3)}`);
};
for (const k of ["do_nothing", "tech_only", "people_only", "clk_v1", "clk_v2"]) {
  const out = M.simulate(p, M.POLICIES[k]);
  close(`${k}: cost index 2030 (2025 prices)`, M.annual(out, "cost_idx_real", 2030), R.summary[k].real);
  close(`${k}: scrap 2030`, M.annual(out, "scrap", 2030) * 100, R.summary[k].scrap);
  close(`${k}: L3+ end-2030`, M.at(out, "S", 2031), R.summary[k].S);
  if (k !== "do_nothing") {
    const e = M.economics(p, M.POLICIES[k], base, out, frozen);
    close(`${k}: NPV vs do-nothing`, e.npv, R.econ[k].npv);
    close(`${k}: NPV vs frozen 2025`, e.npvFrozen, R.econ[k].npv_frozen);
    if (k === "clk_v2") close("clk_v2: CO2 avoided 2030 (t)", e.tco2.find((r) => r.year === 2030).tco2, R.env.find((r) => r.year === 2030).tco2, 1);
  }
}
console.log(fails ? `\n${fails} mismatch(es)` : "\nbrowser model matches the Python model");
process.exit(fails ? 1 : 0);
