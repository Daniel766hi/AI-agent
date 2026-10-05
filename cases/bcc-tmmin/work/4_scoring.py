"""Stage 4 scoring. Run: python work/4_scoring.py

Scores (1-5) are TEAM JUDGMENT; the reason for each sits in work/4_scoring.md.
The weight-sensitivity check asks whether the choice survives anyone's weights,
not only ours.
"""
import numpy as np

CRITERIA = [  # (key, label, weight)
    ("cq", "Dampak biaya & kualitas", 0.20),
    ("lr", "Menaikkan laju belajar", 0.15),
    ("fx", "Fleksibilitas multi-pathway", 0.15),
    ("pk", "Manusia & pengetahuan", 0.15),
    ("hc", "Sulit dibeli/ditiru", 0.10),
    ("fe", "Layak Rp40-120 M & 2026-2030", 0.15),
    ("fit", "Sesuai casebook (bukan alat)", 0.10),
]
W = np.array([c[2] for c in CRITERIA])
assert abs(W.sum() - 1) < 1e-9

#             cq lr fx pk hc fe fit
OPTIONS = {
    "CLK v2 (A+B+C+D+E+H+I+J+K+L)": [5, 5, 4, 5, 5, 3, 5],
    "A Closed-Loop Jidoka":          [5, 3, 2, 3, 4, 4, 5],
    "B Plug-and-Produce":            [3, 3, 5, 2, 5, 3, 4],
    "C Citizen AI Tools":            [3, 4, 3, 5, 4, 4, 5],
    "D Shop-Floor O-Beya":           [2, 4, 2, 5, 4, 5, 4],
    "E Simulation-First":            [2, 3, 5, 2, 4, 3, 4],
    "F Conveyor-less + AMR":         [3, 1, 5, 1, 2, 1, 1],
    "G Predictive Maintenance":      [4, 2, 1, 3, 2, 4, 3],
    "H Firefighting Firewall":       [2, 5, 1, 4, 4, 5, 5],
    "I Operator Idea Engine":        [2, 4, 1, 5, 3, 5, 4],
    "J Learning-Rate Governance":    [2, 4, 2, 2, 3, 5, 4],
    "K Digital Skill Academy":       [1, 3, 3, 5, 3, 5, 3],
    "L Energy Data Loop":            [2, 2, 1, 2, 3, 5, 4],
}
names = list(OPTIONS)
S = np.array([OPTIONS[n] for n in names], dtype=float)

print("== 1. Weighted totals (team weights)")
tot = S @ W
for i in np.argsort(-tot):
    print(f"  {names[i]:<32} {tot[i]:.2f}")

print("\n== 2. Weight sensitivity: 20,000 random weightings (Dirichlet, alpha=1)")
rng = np.random.default_rng(2026)
Wr = rng.dirichlet(np.ones(len(W)), 20000)
T = S @ Wr.T                                  # options x draws
rank1 = np.bincount(T.argmax(0), minlength=len(names)) / T.shape[1]
for i in np.argsort(-rank1):
    if rank1[i] > 0:
        print(f"  {names[i]:<32} ranked #1 in {rank1[i]:.1%} of weightings")

print("\n== 3. Same test without the integrated option (which single lever is strongest?)")
T2 = T[1:]
rank1b = np.bincount(T2.argmax(0), minlength=len(names) - 1) / T2.shape[1]
for i in np.argsort(-rank1b)[:4]:
    print(f"  {names[i + 1]:<32} ranked #1 in {rank1b[i]:.1%}")

print("\n== 4. Penalty test: how low can CLK v2 feasibility go before it loses #1?")
for fe in (3, 2, 1):
    s = S.copy(); s[0, 5] = fe
    t = s @ W
    print(f"  feasibility={fe}: CLK v2 {t[0]:.2f}, best single {t[1:].max():.2f} ({names[1 + t[1:].argmax()]})")

# ---- Pilot area choice
PCRIT = [("imp", "Dampak (heat map Stage 2)", 0.25), ("sig", "Sinyal jelas & terukur", 0.20),
         ("rdy", "Aset sudah ada", 0.15), ("spd", "Terbukti sebelum gate 2027", 0.20),
         ("rsk", "Risiko orang & lingkup (5=rendah)", 0.10), ("yok", "Bisa disalin (yokoten)", 0.10)]
PW = np.array([c[2] for c in PCRIT]); assert abs(PW.sum() - 1) < 1e-9
#                                   imp sig rdy spd rsk yok
PILOTS = {"Sealer -> inspeksi":      [4, 5, 5, 5, 4, 4],
          "Final assembly -> inspeksi": [5, 3, 3, 2, 2, 4],
          "Painting -> inspeksi":    [3, 3, 3, 3, 4, 3],
          "Maintenance (data mesin)": [3, 4, 2, 3, 4, 4],
          "Intralogistics -> final assembly": [3, 3, 3, 3, 3, 3]}
pn = list(PILOTS); P = np.array([PILOTS[n] for n in pn], dtype=float)
print("\n== 5. Pilot area (team weights)")
pt = P @ PW
for i in np.argsort(-pt):
    print(f"  {pn[i]:<34} {pt[i]:.2f}")
PT = P @ rng.dirichlet(np.ones(len(PW)), 20000).T
r1 = np.bincount(PT.argmax(0), minlength=len(pn)) / PT.shape[1]
for i in np.argsort(-r1):
    if r1[i] > 0:
        print(f"  {pn[i]:<34} #1 in {r1[i]:.1%} of random weightings")
imp_only = P[:, 0]
print(f"  If only impact counted: {pn[int(imp_only.argmax())]}")
