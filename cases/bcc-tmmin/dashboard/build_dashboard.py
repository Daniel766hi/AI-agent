"""Build dashboard/index.html: the template with the browser model and the model
results inlined, so the page is one self-contained file.

Run from the case root:  node dashboard/check_parity.js && python dashboard/build_dashboard.py
"""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
R = json.loads((HERE.parent / "model" / "sd_results.json").read_text())
# Financial-model stress test (model/run_tests.py); work/8_tieout.py checks the same values
XL = {"pPlan": 0.86, "pNoGate": 0.73, "pFront": 0.49, "pLate": 0.32}
data = {"params": R["params"], "mc": {k: {kk: v[kk] for kk in ("p_pos", "p5", "p50", "p95", "gate_stop")}
                                      for k, v in R["mc"].items()}, "xl": XL}
html = (HERE / "template.html").read_text()
for anchor, value in (("/*__SD_MODEL__*/", (HERE / "sd_model.js").read_text()),
                      ("/*__DATA__*/", json.dumps(data, separators=(",", ":")))):
    assert html.count(anchor) == 1, anchor
    html = html.replace(anchor, value)
(HERE / "index.html").write_text(html)
print(f"wrote dashboard/index.html ({len(html) // 1024} KB)")
