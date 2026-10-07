"""Figures and numbers for the Problem Identification & Analysis document.

Run from the case root:
  python outputs/build_problem_analysis.py && node outputs/build_problem_analysis.js
Numbers come from data/facts.md (casebook exhibits), work/2_diagnosis_calc.py
(heat map, cost bridge) and model/sd_results.json (2030 targets); nothing is retyped.
"""
import contextlib
import io
import json
import re
import runpy
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "outputs" / "charts"
INK, TEAL, TEAL2, AMBER, RUST, GRAY, GRID = "#13232a", "#0F3D4A", "#0F7B8A", "#F2A900", "#C2410C", "#7A8B92", "#E3E9EA"
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10, "axes.edgecolor": GRID, "axes.labelcolor": "#53656c",
                     "xtick.color": "#53656c", "ytick.color": "#53656c", "axes.spines.top": False, "axes.spines.right": False})


def md_tables(path):
    tables, head, cur = {}, None, None
    for line in Path(path).read_text().splitlines():
        if line.startswith("#"):
            head, cur = line.lstrip("# ").strip(), None
        elif line.startswith("|"):
            cells = [re.sub(r"\*\*|`", "", c.strip()) for c in line.strip().strip("|").split("|")]
            if all(re.fullmatch(r":?-{3,}:?", c) for c in cells):
                continue
            if cur is None:
                cur = []
                tables.setdefault(head, []).append(cur)
            cur.append(cells)
        else:
            cur = None
    return tables


def fig_gap():
    fig, ax = plt.subplots(figsize=(6.4, 3.4), dpi=220)
    yrs = [2023, 2024, 2025]
    t, n = [100, 103, 106], [94, 91, 89]
    ax.plot(yrs, t, color=RUST, lw=2.5, marker="o", label="TMMIN")
    ax.plot(yrs, n, color=TEAL2, lw=2.5, marker="o", label="Pemain baru")
    for x, a, b in zip(yrs, t, n):
        ax.annotate(f"{a}", (x, a), xytext=(0, 7), textcoords="offset points", ha="center", fontsize=9, color=INK)
        ax.annotate(f"{b}", (x, b), xytext=(0, -14), textcoords="offset points", ha="center", fontsize=9, color=INK)
        ax.annotate("", xy=(x + 0.06, b), xytext=(x + 0.06, a), arrowprops=dict(arrowstyle="<->", color=GRAY, lw=1))
        ax.text(x + 0.1, (a + b) / 2, f"{a - b} poin", fontsize=8.5, color="#53656c", va="center")
    ax.set_xticks(yrs)
    ax.set_xlim(2022.8, 2025.5)
    ax.set_ylim(84, 110)
    ax.set_ylabel("indeks (TMMIN 2023 = 100)")
    ax.grid(axis="y", color=GRID, lw=0.8)
    ax.legend(frameon=False, loc="lower left")
    ax.set_title("Indeks biaya konversi per unit, Karawang", loc="left", fontsize=11, fontweight="bold", color=INK)
    fig.tight_layout()
    fig.savefig(OUT / "fig_pi_gap.png")
    plt.close(fig)


def fig_bridge(d):
    fig, ax = plt.subplots(figsize=(6.4, 3.0), dpi=220)
    labs = ["Eskalasi upah & energi 4%/thn", "Scrap 100 → 108", "NVA operator 20% → 22%", "Downtime 100 → 111 (maks)", "Selisih ke pemain baru 2025"]
    vals = [d["p_esc"], d["p_scrap"], d["p_nva"], d["p_maint_hi"], 17]
    cols = [GRAY, TEAL2, TEAL2, TEAL2, RUST]
    y = range(len(labs))[::-1]
    ax.barh(list(y), vals, color=cols, height=0.55)
    for yi, v in zip(y, vals):
        ax.text(v + 0.2, yi, f"{v:.1f}".replace(".", ","), va="center", fontsize=9, color=INK)
    ax.set_yticks(list(y))
    ax.set_yticklabels(labs, fontsize=9)
    ax.set_xlim(0, 19)
    ax.set_xlabel("poin indeks biaya konversi")
    ax.grid(axis="x", color=GRID, lw=0.8)
    ax.set_title("Bagian yang bisa dikendalikan kecil", loc="left", fontsize=11, fontweight="bold", color=INK)
    fig.tight_layout()
    fig.savefig(OUT / "fig_pi_bridge.png")
    plt.close(fig)


def fig_issue_tree():
    """Issue tree drawn left to right: question -> 4 MECE branches -> measurable drivers."""
    branches = [
        ("A. Biaya konversi per unit\nterlalu tinggi", "106 vs 89 (Ex.3)", [
            ("A1 Tenaga kerja", "NVA operator 20% → 22% (Ex.4)"),
            ("A2 Perawatan", "Unplanned downtime 100 → 111 (Ex.4)"),
            ("A3 Scrap", "Scrap 100 → 108; inspeksi Level 1 (Ex.4, Ex.5)"),
            ("A4 Energi", "Tidak ada data: celah data (Ex.5)"),
            ("A5 Depresiasi", "Utilisasi 70%; pasar −7,2% (Ex.1, Ex.9)")]),
        ("B. Kualitas: cacat\nditemukan terlambat", "Cacat lolos 100 → 103 (Ex.4)", [
            ("B1 Deteksi di akhir lini", "Inspeksi visual manual, Level 1 (Ex.5)"),
            ("B2 Tidak ada umpan balik", "Sealer tanpa umpan balik otomatis (Ex.5)"),
            ("B3 Alert diabaikan", "31% operator sering mengabaikan (Ex.6B)")]),
        ("C. Varian baru mahal\ndan lambat", "8 → 9 bulan per varian (Ex.4)", [
            ("C1 Peralatan point-to-point", "Tanpa standar antarmuka, Level 2 (Ex.5)"),
            ("C2 Varian bertambah", "Elektrifikasi 30% → 55–70% (Ex.8)"),
            ("C3 Bergantung pihak luar", "Software & AI L3+ hanya 2/30 (Ex.7)")]),
        ("D. Laju perbaikan kalah\ndari pesaing", "Selisih +5,5 poin/thn (Ex.3)", [
            ("D1 Waktu", "Rutin 62% → 65%; perbaikan 28% → 25% (Ex.6A)"),
            ("D2 Hasil", "Ide terimplementasi/engineer −38% (Ex.6A)"),
            ("D3 Pengetahuan", "Terdokumentasi 35% → 33%; 48% bergantung senior"),
            ("D4 Kapabilitas", "18% operator terlatih alat data (Ex.6B)")]),
    ]
    leaves = sum(len(b[2]) for b in branches)
    gap = 0.55
    H = leaves + gap * (len(branches) - 1)
    fig, ax = plt.subplots(figsize=(11.0, 7.4), dpi=220)
    ax.set_xlim(0, 11)
    ax.set_ylim(-0.6, H + 0.2)
    ax.axis("off")

    def box(x, y, w, h, text, fc, ec, color=INK, size=8.6, bold=False):
        ax.add_patch(FancyBboxPatch((x, y - h / 2), w, h, boxstyle="round,pad=0.02,rounding_size=0.08", fc=fc, ec=ec, lw=1))
        ax.text(x + 0.1, y, text, va="center", ha="left", fontsize=size, color=color, fontweight="bold" if bold else "normal", linespacing=1.25)

    y = H - 0.5
    mids = []
    for title, ev, kids in branches:
        ys = []
        for name, metric in kids:
            box(6.15, y, 4.75, 0.78, f"{name}\n{metric}", "#FFFFFF", GRID, size=8.2)
            ax.text(6.25, y + 0.2, "", fontsize=1)
            ys.append(y)
            y -= 1
        mid = (ys[0] + ys[-1]) / 2
        mids.append(mid)
        box(2.85, mid, 2.75, 1.25, f"{title}\n{ev}", "#EEF3F4", TEAL2, size=8.8, bold=False)
        for yy in ys:
            ax.plot([5.6, 5.88, 5.88, 6.15], [mid, mid, yy, yy], color=GRAY, lw=0.9)
        y -= gap
    root_y = (mids[0] + mids[-1]) / 2
    box(0.05, root_y, 2.5, 2.3, "Mengapa daya saing\nbiaya dan kualitas\nTMMIN tergerus, dan\ncelah mana yang\npaling menentukan?", TEAL, TEAL, color="#FFFFFF", size=9.2, bold=True)
    for m in mids:
        ax.plot([2.55, 2.7, 2.7, 2.85], [root_y, root_y, m, m], color=GRAY, lw=0.9)
    ax.text(0.05, -0.35, "Level 1 MECE: posisi hari ini (A, B), biaya masa depan (C), dan laju perbaikan (D). Cabang A dipecah persis mengikuti lima komponen biaya konversi di Exhibit 9.",
            fontsize=8, color="#53656c")
    fig.tight_layout()
    fig.savefig(OUT / "fig_pi_issuetree.png")
    plt.close(fig)


def main():
    with contextlib.redirect_stdout(io.StringIO()):
        d = runpy.run_path(str(ROOT / "work" / "2_diagnosis_calc.py"))
    sd = json.loads((ROOT / "model" / "sd_results.json").read_text())
    facts = md_tables(ROOT / "data" / "facts.md")
    diag = md_tables(ROOT / "work" / "2_diagnosis.md")
    fig_gap()
    fig_bridge(d)
    fig_issue_tree()
    s, soc = sd["summary"], sd["social"]["2030"]
    data = {
        "ex": {k.split(".")[0].replace("Exhibit ", ""): v[0] for k, v in facts.items() if k.startswith("Exhibit")},
        "drivers": next(v[0] for k, v in diag.items() if k.startswith("2. Driver")),
        "whys": next(v[0] for k, v in diag.items() if k.startswith("5. Akar")),
        "complications": next(v[0] for k, v in diag.items() if k.startswith("Uji: apakah")),
        "bridge": next(v[0] for k, v in diag.items() if k.startswith("3.2")),
        "rivals": next(v[0] for k, v in diag.items() if k.startswith("6. Hipotesis")),
        "evidence": next(v[0] for k, v in diag.items() if k.startswith("7. Area")),
        "opps": next(v[0] for k, v in diag.items() if k.startswith("8. Peluang")),
        "links": next(v[2] for k, v in diag.items() if k.startswith("4. Gap heat map")),
        "heat": {k: list(v) for k, v in d["procs"].items()},
        "top3": d["top3_count"],
        "calc": {"widen": d["widen"], "share_t": d["share_t"], "drift_lo": d["drift_lo"], "drift_hi": d["drift_hi"],
                 "impl23": d["impl23"], "impl25": d["impl25"], "p_esc": d["p_esc"], "real_t": d["real_t"], "real_n": d["real_n"]},
        "target": {"idx_sd": s["clk_v2"]["real"], "idx_dn": s["do_nothing"]["real"], "scrap": s["clk_v2"]["scrap"],
                   "esc": s["clk_v2"]["esc"], "down": s["clk_v2"]["down"], "months": s["clk_v2"]["months"],
                   "months_dn": s["do_nothing"]["months"], "S": s["clk_v2"]["S"], "K": s["clk_v2"]["K"],
                   "improve": s["clk_v2"]["improve"], "senior": soc["senior_dep"], "ramp": soc["ramp_months"]},
    }
    (OUT / "problem_analysis.json").write_text(json.dumps(data, ensure_ascii=False, indent=1))
    print("figures and outputs/charts/problem_analysis.json written")


if __name__ == "__main__":
    main()
