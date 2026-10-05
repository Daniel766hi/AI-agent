from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.chart import BarChart, Reference
from openpyxl.utils import get_column_letter as L

wb = Workbook()
F = "Arial"
BLUE = Font(name=F, color="0000FF", size=10)
BLACK = Font(name=F, color="000000", size=10)
GREEN = Font(name=F, color="008000", size=10)
BOLD = Font(name=F, bold=True, size=10)
TITLE = Font(name=F, bold=True, size=14, color="1F3864")
H2 = Font(name=F, bold=True, size=11, color="FFFFFF")
HFILL = PatternFill("solid", fgColor="1F3864")
SUB = PatternFill("solid", fgColor="D9E1F2")
YEL = PatternFill("solid", fgColor="FFFF00")
RED = PatternFill("solid", fgColor="F8CBAD")
GRN = PatternFill("solid", fgColor="E2EFDA")
WRAP = Alignment(wrap_text=True, vertical="top")
thin = Side(style="thin", color="BFBFBF")
BOX = Border(left=thin, right=thin, top=thin, bottom=thin)
PCT = '0.0%;(0.0%);"-"'
RP = '#,##0.0;(#,##0.0);"-"'
RP0 = '#,##0;(#,##0);"-"'


def cell(ws, ref, v, font=BLACK, fill=None, fmt=None, wrap=False, border=False):
    c = ws[ref]
    c.value = v
    c.font = font
    if fill:
        c.fill = fill
    if fmt:
        c.number_format = fmt
    if wrap:
        c.alignment = WRAP
    if border:
        c.border = BOX
    return c


def header_row(ws, row, labels, start_col=1):
    for i, lab in enumerate(labels):
        c = ws.cell(row=row, column=start_col + i, value=lab)
        c.font = H2
        c.fill = HFILL
        c.alignment = Alignment(wrap_text=True, vertical="center")
        c.border = BOX


def widths(ws, ws_widths):
    for col, w in ws_widths.items():
        ws.column_dimensions[col].width = w


def text_table(ws, start_row, headers, rows, wrap=True, height=None):
    header_row(ws, start_row, headers)
    for r, data in enumerate(rows, start=start_row + 1):
        for ci, v in enumerate(data, start=1):
            c = ws.cell(row=r, column=ci, value=v)
            c.font = BOLD if ci == 1 else BLACK
            c.alignment = WRAP
            c.border = BOX
        if height:
            ws.row_dimensions[r].height = height
    return start_row + len(rows) + 1


# ------------------------------------------------------------------ README
ws = wb.active
ws.title = "README"
cell(ws, "A1", "TMMIN Next-Level Kaizen: Case Model & Answer Kit", TITLE)
cell(ws, "A2", "Working file for the team. Every number traces to a case exhibit or a labeled assumption.", BLACK)
cell(ws, "A4", "Colour legend", BOLD)
cell(ws, "A5", "Blue text", BLUE); cell(ws, "B5", "Hardcoded input (from the case or a team assumption)")
cell(ws, "A6", "Black text", BLACK); cell(ws, "B6", "Formula, do not overwrite")
cell(ws, "A7", "Green text", GREEN); cell(ws, "B7", "Link from another tab")
cell(ws, "A8", "Yellow fill", BLACK, YEL); cell(ws, "B8", "Key assumption the team must justify or change")
cell(ws, "A9", "Red fill", BLACK, RED); cell(ws, "B9", "VERIFY against the original casebook PDF (text came through garbled)")
cell(ws, "A11", "Tab map", BOLD)
tabs = [
    ("WBS", "Work breakdown: who does what, which day, done criteria, hours, daily Gantt. Start here."),
    ("Answer_Guide", "How to answer each sub-question, deck storyline with action titles, Q&A prep"),
    ("Ideation", "8 idea options with case gaps, TPS anchor, Toyota precedent, references, weighted scoring"),
    ("Simulation", "Idea tests run in Python: closed-loop quality sim, financial Monte Carlo, roadmap strategies, tornado"),
    ("Exhibits", "Clean re-typed case data (Exhibits 1, 3-9). Fix red cells first"),
    ("Assumptions", "All model inputs + benchmark evidence for each lever; pilot-light phasing"),
    ("Model", "Savings by lever, investment, running cost, NPV, IRR, payback for 3 scenarios (2026-2030)"),
    ("Dashboard", "Scenario summary and charts for the financial slide"),
    ("Breakeven", "How much saving pays back Rp40-120B, plus NPV sensitivity grid"),
    ("Capability", "Workforce model: engineer skill levels, improvement time, know-how, ramp-up to 2030"),
    ("KPIs", "KPI tree with baselines from exhibits and suggested pilot / 2030 targets"),
    ("Roadmap", "Phased 2026-2030 roadmap template across workstreams"),
    ("Risks", "Risk register with mitigations, early-warning KPIs and evidence"),
    ("QA_Bank", "15 likely judge questions with answer outline, evidence and owner"),
]
for i, (t, d) in enumerate(tabs, start=12):
    cell(ws, f"A{i}", t, BOLD); cell(ws, f"B{i}", d)
hr = 12 + len(tabs) + 1
cell(ws, f"A{hr}", "How to use", BOLD)
steps = [
    "1. Day 1: type names in WBS, re-type every red cell in Exhibits from the PDF.",
    "2. Day 2-3: re-score Ideation as a team, lock ONE integrated idea + one pilot area by end of Day 3.",
    "3. Day 3-4: replace yellow assumptions with numbers you can defend (Assumptions column G shows benchmarks found so far).",
    "4. Day 5: re-run run_tests.py so the Simulation tab matches your final assumptions.",
    "5. Dashboard, Breakeven and Capability update automatically. Example values in yellow cells are placeholders, not facts.",
]
for i, s_ in enumerate(steps, start=hr + 1):
    cell(ws, f"A{i}", s_)
widths(ws, {"A": 18, "B": 100})

# ------------------------------------------------------------------ EXHIBITS
ex = wb.create_sheet("Exhibits")
cell(ex, "A1", "Case exhibits, re-typed (verify red cells against the PDF)", TITLE)
r = 3
cell(ex, f"A{r}", "Exhibit 1. National car sales (units)", BOLD); r += 1
header_row(ex, r, ["Metric", "2024", "2025", "Change"]); r += 1
for name, a, b in [("Wholesales", 865723, 803687), ("Retail sales", 889680, 833692)]:
    cell(ex, f"A{r}", name); cell(ex, f"B{r}", a, BLUE, fmt=RP0); cell(ex, f"C{r}", b, BLUE, fmt=RP0)
    cell(ex, f"D{r}", f"=C{r}/B{r}-1", fmt=PCT); r += 1
r += 1
cell(ex, f"A{r}", "Exhibit 3. Conversion cost index, Karawang (TMMIN 2023 = 100)", BOLD); r += 1
header_row(ex, r, ["Year", "TMMIN", "New-player benchmark", "TMMIN vs benchmark"]); r += 1
e3_start = r
for y, a, b in [("2023", 100, 94), ("2024", 103, 91), ("2025", 106, 89)]:
    cell(ex, f"A{r}", y); cell(ex, f"B{r}", a, BLUE); cell(ex, f"C{r}", b, BLUE)
    cell(ex, f"D{r}", f"=B{r}/C{r}-1", fmt=PCT); r += 1
r += 1
cell(ex, f"A{r}", "Exhibit 4. Quality & productivity baseline (index 2023 = 100 unless stated)", BOLD); r += 1
header_row(ex, r, ["Metric", "2023", "2025", "Note"]); r += 1
e4 = [
    ("Scrap (index)", 100, 108, "Verified from casebook PDF"),
    ("Unplanned downtime (index)", 100, 111, "Verified from casebook PDF"),
    ("Defects escaping to downstream (index)", 100, 103, "Verified from casebook PDF"),
    ("Operator non-value-added time (% hours)", 0.20, 0.22, "Verified from casebook PDF"),
    ("Equipment modification time, new variant (months)", 8, 9, "Verified from casebook PDF"),
]
for name, a, b, note in e4:
    cell(ex, f"A{r}", name)
    for col, v in (("B", a), ("C", b)):
        if v == "VERIFY":
            cell(ex, f"{col}{r}", v, BLACK, RED)
        else:
            cell(ex, f"{col}{r}", v, BLUE, fmt=PCT if isinstance(v, float) and v < 1 else None)
    cell(ex, f"D{r}", note, wrap=True); r += 1
r += 1
cell(ex, f"A{r}", "Exhibit 5. Automation maturity (1 manual, 2 semi-auto, 3 auto+integrated, 4 autonomous)", BOLD); r += 1
header_row(ex, r, ["Process", "Level", "Gap to L4", "Key condition"]); r += 1
e5 = [
    ("Press shop", 3, "Die changes and panel quality checks rely on operators"),
    ("Casting", 2, "Finishing, handling, inspection partly manual"),
    ("Machining & engine assembly", 3, "Assembly and inspection partly manual"),
    ("Body welding: spot welding", 3, "Programmed robots integrated in line"),
    ("Body welding: sealer application", 2, "Manual/semi-auto; no automatic quality feedback"),
    ("Painting", 3, "Quality check and defect repair manual visual"),
    ("Final assembly", 2, "Manual with tools; high variant mix handled by operators"),
    ("Quality inspection", 1, "Manual visual; in-house AI camera (from CCTV) in validation to Oct 2026"),
    ("Intralogistics", 2, "Manual forklifts/dollies; AGV/AMR pilots"),
    ("Maintenance", 2, "Periodic preventive, not predictive"),
    ("Equipment & system integration", 2, "Point-to-point; no common interface standard"),
    ("Data integration", 1, "Data scattered; equipment, quality, logistics not connected"),
]
for name, lv, note in e5:
    cell(ex, f"A{r}", name)
    if lv == "VERIFY":
        cell(ex, f"B{r}", lv, BLACK, RED)
        cell(ex, f"C{r}", "VERIFY", BLACK, RED)
    else:
        cell(ex, f"B{r}", lv, BLUE)
        cell(ex, f"C{r}", f"=4-B{r}")
    cell(ex, f"D{r}", note, wrap=True); r += 1
r += 1
cell(ex, f"A{r}", "Exhibit 6A. Engineering time, knowledge & improvement (production engineering)", BOLD); r += 1
header_row(ex, r, ["Metric", "2023", "2025", "Note"]); r += 1
e6a = [
    ("Engineer time on routine support & troubleshooting (%)", 0.62, 0.65, "Verified; the remaining ~10% is other work"),
    ("Engineer time on improvement & new development (%)", 0.28, 0.25, ""),
    ("Critical know-how documented in shared form (%)", 0.35, 0.33, ""),
    ("Critical processes whose know-how rests with 1-2 seniors (%)", 0.45, 0.48, ""),
    ("Months for new engineer to work independently", 14, 15, ""),
    ("Improvement ideas per engineer per year", 3.1, 2.4, ""),
    ("Ideas implemented (% of submitted)", 0.35, 0.28, ""),
]
for name, a, b, note in e6a:
    cell(ex, f"A{r}", name, wrap=True)
    for col, v in (("B", a), ("C", b)):
        if v == "VERIFY":
            cell(ex, f"{col}{r}", v, BLACK, RED)
        else:
            cell(ex, f"{col}{r}", v, BLUE, fmt=PCT if isinstance(v, float) and v < 1 else None)
    cell(ex, f"D{r}", note, wrap=True); r += 1
r += 1
cell(ex, f"A{r}", "Exhibit 6B. Operator & team-leader perception, pilot area (2025, N = 120)", BOLD); r += 1
header_row(ex, r, ["Indicator", "Share", "", "So what"]); r += 1
e6b = [
    ("Say new tech helps rather than replaces their work", 0.54, "46% are not convinced: change management is a real risk"),
    ("Have received training on data-driven tools", 0.18, "Training gap is the biggest adoption blocker"),
    ("Frequently override or ignore automated alerts", 0.31, "Tech without trust = no value; design alerts with operators"),
    ("Know-how shared mainly via informal on-the-job coaching", 0.71, "Supports knowledge-capture idea"),
    ("Would contribute ideas if an easy channel existed", 0.62, "Latent kaizen energy: biggest people opportunity"),
]
for name, v, note in e6b:
    cell(ex, f"A{r}", name, wrap=True)
    if v == "VERIFY":
        cell(ex, f"B{r}", v, BLACK, RED)
    else:
        cell(ex, f"B{r}", v, BLUE, fmt=PCT)
    cell(ex, f"D{r}", note, wrap=True); r += 1
r += 1
cell(ex, f"A{r}", "Exhibit 7. Engineering competence (members per level, N = 30 per field)", BOLD); r += 1
header_row(ex, r, ["Field", "L1 basic", "L2 intermediate", "L3 proficient", "L4 expert", "Total", "% at L3+"]); r += 1
e7 = [("Mechanical", 3, 8, 14, 5), ("Electrical", 5, 10, 11, 4), ("PLC", 7, 11, 9, 3),
      ("Programming", 14, 10, 5, 1), ("Software & AI", 20, 8, 2, 0)]
for name, *lv in e7:
    cell(ex, f"A{r}", name)
    for i, v in enumerate(lv):
        cell(ex, f"{L(2+i)}{r}", v, BLUE)
    cell(ex, f"F{r}", f"=SUM(B{r}:E{r})")
    cell(ex, f"G{r}", f"=(D{r}+E{r})/F{r}", fmt=PCT); r += 1
cell(ex, f"A{r}", "Verified from casebook PDF", wrap=False); r += 2
cell(ex, f"A{r}", "Exhibit 8. Volume share by pathway (indicative)", BOLD); r += 1
header_row(ex, r, ["Pathway", "2026", "2030 moderate", "2030 aggressive"]); r += 1
e8s = r
for name, a, b, c in [("Conventional (ICE)", .70, .45, .30), ("HEV", .25, .38, .40), ("PHEV", .03, .07, .10), ("BEV", .02, .10, .20)]:
    cell(ex, f"A{r}", name)
    for col, v in (("B", a), ("C", b), ("D", c)):
        cell(ex, f"{col}{r}", v, BLUE, fmt=PCT)
    r += 1
cell(ex, f"A{r}", "Electrified share (HEV+PHEV+BEV)", BOLD)
for col in "BCD":
    cell(ex, f"{col}{r}", f"=SUM({col}{e8s+1}:{col}{r-1})", fmt=PCT)
r += 2
cell(ex, f"A{r}", "Exhibit 9 parameters are in the Assumptions tab (rows 4-15).", BOLD)
widths(ex, {"A": 52, "B": 13, "C": 15, "D": 55, "E": 11, "F": 9, "G": 10})

# ------------------------------------------------------------------ ASSUMPTIONS
a = wb.create_sheet("Assumptions")
cell(a, "A1", "Model inputs", TITLE)
header_row(a, 3, ["Case parameter (Exhibit 9 / text)", "Value", "Unit", "Source / note"])
base = [
    (4, "Installed capacity, Karawang I + II", 250000, "units/yr", "Exhibit 9", RP0),
    (5, "Capacity utilization 2025", 0.70, "%", "Exhibit 9", PCT),
    (6, "Production volume", "=B4*B5", "units/yr", "Formula (case: ~175,000)", RP0),
    (7, "Conversion cost per unit 2025", 3.2, "Rp million", "Exhibit 9 (labor, energy, maintenance, depreciation, scrap)", RP),
    (8, "Total annual conversion cost", "=B6*B7/1000", "Rp billion", "Formula (case: ~Rp560B)", RP),
    (9, "Discount rate", 0.10, "%/yr", "Exhibit 9", PCT),
    (10, "Labor & energy cost escalation", 0.04, "%/yr", "Exhibit 9, applied to savings", PCT),
    (11, "Technology economic life", 5, "years", "Exhibit 9", None),
    (12, "TMMIN conversion cost index 2025", 106, "index", "Exhibit 3", None),
    (13, "New-player benchmark index 2025", 89, "index", "Exhibit 3", None),
    (14, "Operator non-value-added time", 0.22, "% hours", "Exhibit 4 / text", PCT),
    (15, "Equipment modification time per new variant", 9, "months", "Exhibit 4 / text", None),
]
for row, lab, v, unit, src, fmt in base:
    cell(a, f"A{row}", lab)
    is_formula = isinstance(v, str) and v.startswith("=")
    cell(a, f"B{row}", v, BLACK if is_formula else BLUE, fmt=fmt)
    cell(a, f"C{row}", unit); cell(a, f"D{row}", src, wrap=True)

header_row(a, 17, ["Conversion cost split (TEAM ASSUMPTION, case gives components only)", "Share", "Rp billion", "Justify with"])
split = [(18, "Labor"), (19, "Energy"), (20, "Maintenance"), (21, "Depreciation"), (22, "Scrap")]
vals = [0.40, 0.12, 0.13, 0.25, 0.10]
for (row, lab), v in zip(split, vals):
    cell(a, f"A{row}", lab); cell(a, f"B{row}", v, BLUE, YEL, PCT)
    cell(a, f"C{row}", f"=B{row}*$B$8", fmt=RP)
    cell(a, f"D{row}", "No public source splits conversion cost. Stated team assumption; Monte Carlo tests labor share 35-45% (Simulation tab). Ask organizers in clarification if allowed.", wrap=True)
cell(a, "A23", "Check (must be 100%)", BOLD); cell(a, "B23", "=SUM(B18:B22)", fmt=PCT); cell(a, "C23", "=SUM(C18:C22)", fmt=RP)

header_row(a, 25, ["Other team assumptions", "Value", "Unit", "Note"])
other = [
    (26, "New variant / model-change projects per year", 3, "projects/yr", "Rises with multi-pathway mix (Exhibit 8)", None),
    (27, "Average cost per equipment modification project", 10, "Rp billion", "Team assumption, no public source. Tornado shows its NPV swing (Simulation Test 3); state it openly.", RP),
    (28, "Share of freed operator time converted to cash", 0.50, "%", "Rest is redeployed to kaizen / absorbs volume (no layoffs)", PCT),
]
for row, lab, v, unit, note, fmt in other:
    cell(a, f"A{row}", lab); cell(a, f"B{row}", v, BLUE, YEL, fmt)
    cell(a, f"C{row}", unit); cell(a, f"D{row}", note, wrap=True)

header_row(a, 31, ["Lever assumptions by scenario", "Conservative", "Base", "Optimistic", "What drives it / how to defend", "", "Benchmark evidence (cite in appendix)"])
levers = [
    (32, "Scrap cost reduction", (0.20, 0.35, 0.50), PCT, "Closed-loop feedback catches sealer/inspection lapses upstream (Exhibit 4/5)",
     "Own simulation (Simulation tab): closed loop cuts in-scope scrap ~85%; x 40% scope share = ~34% plant-wide. Base 35% sits on that result."),
    (33, "Maintenance cost reduction", (0.05, 0.10, 0.15), PCT, "Predictive maintenance + fewer unplanned stops",
     "McKinsey (2020, via IIoT World): maintenance cost -18 to 25%, unplanned downtime up to -50%. Our range is deliberately below. https://www.iiot-world.com/predictive-analytics/predictive-maintenance/predictive-maintenance-cost-savings/"),
    (34, "Operator NVA time eliminated (% of the 22%)", (0.15, 0.30, 0.45), PCT, "Intralogistics sync, digital standard work, less searching/waiting",
     "Toyota AI Platform: >10,000 man-hours/yr saved by worker-built tools (Google Cloud 2024). Omron/MPA AMR case: up to 15 km/day of operator walking and all manual crate runs eliminated (no % published). Validate with a time study in the pilot. https://robotics.omron.com/case-studies/amr-automation-intralogistics-mpa-omron/"),
    (35, "Energy cost reduction", (0.02, 0.05, 0.08), PCT, "Data-driven idle/standby control",
     "Nissan US plants, energy management system (ISO 50001 / SEP): 13.8% energy performance gain over 3 years, 8-21% by site. Our 2-8% is deliberately below. https://www.cleanenergyministerial.org/content/uploads/2022/03/cem-em-casestudy-nissan-usa.pdf"),
    (36, "Variant modification cost reduction", (0.20, 0.35, 0.50), PCT, "Common interface standard + in-house equipment + virtual verification",
     "Siemens / Wipro PARI: virtual commissioning cut on-site commissioning 70% on a 17-variant engine line. Kalypso: up to 40%. Toyota BEV plan targets halving prep lead time. https://resources.sw.siemens.com/en-US/case-study-wipro-pari/"),
    (37, "Total program investment", (110, 80, 60), RP, "Must sit inside case range Rp40-120B", "Case Exhibit 9"),
    (38, "Annual running cost (% of cumulative investment)", (0.10, 0.10, 0.08), PCT, "Licences, cloud/compute, upkeep", "Team assumption"),
    (39, "Training & change management opex", (3.0, 2.5, 2.0), RP, "Rp billion/yr: academy, coaches, kaizen time", "Team assumption; cross-check with Capability tab"),
]
for row, lab, (c1, c2, c3), fmt, note, bench in levers:
    cell(a, f"A{row}", lab, wrap=True)
    for col, v in zip("BCD", (c1, c2, c3)):
        cell(a, f"{col}{row}", v, BLUE, YEL, fmt)
    cell(a, f"E{row}", note, wrap=True)
    cell(a, f"G{row}", bench, wrap=True)
    a.row_dimensions[row].height = 54
cell(a, "A40", "Implied variant modification time (months)")
for col in "BCD":
    cell(a, f"{col}40", f"=$B$15*(1-{col}36)", fmt="0.0")
cell(a, "E40", "Show this on the flexibility slide (vs 9 months today)", wrap=True)

header_row(a, 42, ["Timing", "2026", "2027", "2028", "2029", "2030", "Sum / note"])
cell(a, "A43", "Adoption ramp-up (% of full run-rate)")
for col, v in zip("BCDEF", (0.10, 0.35, 0.65, 0.90, 1.00)):
    cell(a, f"{col}43", v, BLUE, YEL, PCT)
cell(a, "G43", "Pilot -> standardize -> rollout")
cell(a, "A44", "Investment phasing (% of total): PILOT-LIGHT")
for col, v in zip("BCDEF", (0.10, 0.15, 0.40, 0.25, 0.10)):
    cell(a, f"{col}44", v, BLUE, YEL, PCT)
cell(a, "G44", "=SUM(B44:F44)", fmt=PCT)
cell(a, "A45", "Year index (t)")
for i, col in enumerate("BCDEF", start=1):
    cell(a, f"{col}45", i, BLUE)
cell(a, "G45", "End-of-year discounting")
cell(a, "A46", "Reference only: original front-loaded phasing")
for col, v in zip("BCDEF", (0.30, 0.35, 0.25, 0.10, 0.0)):
    cell(a, f"{col}46", v, BLUE, fmt=PCT)
cell(a, "A47", "Why pilot-light: Simulation tab Test 2b. Spending little before the end-2027 gate raised P(NPV>0) from ~49% to ~85% across 10,000 runs.", wrap=False)
widths(a, {"A": 50, "B": 14, "C": 14, "D": 14, "E": 46, "F": 10, "G": 60})
a.freeze_panes = "B4"

# ------------------------------------------------------------------ MODEL
m = wb.create_sheet("Model")
cell(m, "A1", "Savings, investment and NPV by scenario (Rp billion)", TITLE)
cell(m, "A2", "Program window 2026-2030 = 5-year economic life. No terminal value (conservative).", BLACK)
YC = ["C", "D", "E", "F", "G"]          # model year columns
AC = ["B", "C", "D", "E", "F"]          # matching Assumptions columns
outputs = {}


def block(start, scol, name):
    s = start
    cell(m, f"A{s}", f"Scenario: {name}", Font(name=F, bold=True, size=12, color="1F3864"))
    header_row(m, s + 1, ["Line item", "Unit", "2026", "2027", "2028", "2029", "2030", "Total"])
    rows = {
        "ramp": s + 2, "esc": s + 3, "scrap": s + 4, "maint": s + 5, "labor": s + 6,
        "energy": s + 7, "variant": s + 8, "sav": s + 9, "inv": s + 10, "cuminv": s + 11,
        "run": s + 12, "net": s + 13, "df": s + 14, "pv": s + 15, "cum": s + 16,
    }
    labels = {
        "ramp": ("Adoption ramp-up", "%"), "esc": ("Escalation factor", "x"),
        "scrap": ("Saving: scrap", "Rp B"), "maint": ("Saving: maintenance / downtime", "Rp B"),
        "labor": ("Saving: operator NVA time", "Rp B"), "energy": ("Saving: energy", "Rp B"),
        "variant": ("Saving: variant modification", "Rp B"), "sav": ("Total gross savings", "Rp B"),
        "inv": ("Investment (capex)", "Rp B"), "cuminv": ("Cumulative investment", "Rp B"),
        "run": ("Running + training cost", "Rp B"), "net": ("Net cash flow", "Rp B"),
        "df": ("Discount factor", "x"), "pv": ("Present value", "Rp B"), "cum": ("Cumulative net cash flow", "Rp B"),
    }
    for k, rr in rows.items():
        lab, unit = labels[k]
        cell(m, f"A{rr}", lab, BOLD if k in ("sav", "net", "pv") else BLACK)
        cell(m, f"B{rr}", unit)
    A = "Assumptions!"
    for yc, ac in zip(YC, AC):
        R = rows
        cell(m, f"{yc}{R['ramp']}", f"={A}{ac}$43", GREEN, fmt=PCT)
        cell(m, f"{yc}{R['esc']}", f"=(1+{A}$B$10)^({A}{ac}$45-1)", fmt="0.000")
        common = f"*{yc}{R['ramp']}*{yc}{R['esc']}"
        cell(m, f"{yc}{R['scrap']}", f"={A}$B$8*{A}$B$22*{A}${scol}$32{common}", fmt=RP)
        cell(m, f"{yc}{R['maint']}", f"={A}$B$8*{A}$B$20*{A}${scol}$33{common}", fmt=RP)
        cell(m, f"{yc}{R['labor']}", f"={A}$B$8*{A}$B$18*{A}$B$14*{A}${scol}$34*{A}$B$28{common}", fmt=RP)
        cell(m, f"{yc}{R['energy']}", f"={A}$B$8*{A}$B$19*{A}${scol}$35{common}", fmt=RP)
        cell(m, f"{yc}{R['variant']}", f"={A}$B$26*{A}$B$27*{A}${scol}$36{common}", fmt=RP)
        cell(m, f"{yc}{R['sav']}", f"=SUM({yc}{R['scrap']}:{yc}{R['variant']})", BOLD, fmt=RP)
        cell(m, f"{yc}{R['inv']}", f"={A}${scol}$37*{A}{ac}$44", fmt=RP)
        cell(m, f"{yc}{R['cuminv']}", f"=SUM($C{R['inv']}:{yc}{R['inv']})", fmt=RP)
        cell(m, f"{yc}{R['run']}", f"={yc}{R['cuminv']}*{A}${scol}$38+{A}${scol}$39", fmt=RP)
        cell(m, f"{yc}{R['net']}", f"={yc}{R['sav']}-{yc}{R['inv']}-{yc}{R['run']}", BOLD, fmt=RP)
        cell(m, f"{yc}{R['df']}", f"=1/(1+{A}$B$9)^{A}{ac}$45", fmt="0.000")
        cell(m, f"{yc}{R['pv']}", f"={yc}{R['net']}*{yc}{R['df']}", BOLD, fmt=RP)
        cell(m, f"{yc}{R['cum']}", f"=SUM($C{R['net']}:{yc}{R['net']})", fmt=RP)
    for k in ("scrap", "maint", "labor", "energy", "variant", "sav", "inv", "run", "net", "pv"):
        cell(m, f"H{rows[k]}", f"=SUM(C{rows[k]}:G{rows[k]})", BOLD if k in ("sav", "net", "pv") else BLACK, fmt=RP)
    o = s + 18
    cell(m, f"A{o}", "Outputs", BOLD, SUB)
    out = [
        ("NPV @ discount rate", f"=SUM(C{rows['pv']}:G{rows['pv']})", RP, "Rp B"),
        ("IRR", f"=IFERROR(IRR(C{rows['net']}:G{rows['net']}),\"n/a\")", PCT, "%"),
        ("Payback year (cumulative net turns positive)", f"=IF(G{rows['cum']}<0,\"Beyond 2030\",2026+COUNTIF(C{rows['cum']}:G{rows['cum']},\"<0\"))", None, "year"),
        ("Full run-rate savings (2025 prices)",
         f"=Assumptions!$B$8*(Assumptions!$B$22*Assumptions!{scol}32+Assumptions!$B$20*Assumptions!{scol}33"
         f"+Assumptions!$B$18*Assumptions!$B$14*Assumptions!{scol}34*Assumptions!$B$28+Assumptions!$B$19*Assumptions!{scol}35)"
         f"+Assumptions!$B$26*Assumptions!$B$27*Assumptions!{scol}36", RP, "Rp B/yr"),
        ("Run-rate savings as % of conversion cost", f"=C{o+4}/Assumptions!$B$8", PCT, "%"),
        ("Implied conversion cost index", f"=Assumptions!$B$12*(1-C{o+5})", "0.0", "index"),
        ("Share of gap to benchmark closed", f"=(Assumptions!$B$12-C{o+6})/(Assumptions!$B$12-Assumptions!$B$13)", PCT, "%"),
        ("NPV incl. remaining equipment value at end-2030 (book)",
         f"=C{o+1}+SUMPRODUCT(C{rows['inv']}:G{rows['inv']},(Assumptions!$B$45:$F$45-0.5)/Assumptions!$B$11)/(1+Assumptions!$B$9)^Assumptions!$B$11", RP, "Rp B"),
    ]
    for i, (lab, f_, fmt, unit) in enumerate(out, start=1):
        cell(m, f"A{o+i}", lab); cell(m, f"B{o+i}", unit)
        cell(m, f"C{o+i}", f_, BOLD, fmt=fmt)
    outputs[name] = {"npv": f"C{o+1}", "irr": f"C{o+2}", "pb": f"C{o+3}", "rr": f"C{o+4}",
                     "rrp": f"C{o+5}", "idx": f"C{o+6}", "gap": f"C{o+7}", "npvr": f"C{o+8}", "sav2030": f"G{rows['sav']}",
                     "rows": rows}
    return o + len(out) + 2


nxt = block(4, "B", "Conservative")
nxt = block(nxt, "C", "Base")
nxt = block(nxt, "D", "Optimistic")
widths(m, {"A": 42, "B": 9, "C": 12, "D": 12, "E": 12, "F": 12, "G": 12, "H": 12})
m.freeze_panes = "C4"

# ------------------------------------------------------------------ DASHBOARD
d = wb.create_sheet("Dashboard")
cell(d, "A1", "Financial summary for the deck (Rp billion)", TITLE)
header_row(d, 3, ["Metric", "Conservative", "Base", "Optimistic"])
dash = [("NPV (10%)", "npv", RP), ("IRR", "irr", PCT), ("Payback year", "pb", None),
        ("Gross savings in 2030", "sav2030", RP), ("Full run-rate savings / yr", "rr", RP),
        ("Run-rate as % of conversion cost", "rrp", PCT), ("Implied cost index (today 106)", "idx", "0.0"),
        ("Gap to new-player benchmark closed", "gap", PCT), ("NPV incl. remaining equipment value", "npvr", RP)]
for i, (lab, k, fmt) in enumerate(dash, start=4):
    cell(d, f"A{i}", lab, BOLD)
    for col, sc in zip("BCD", ("Conservative", "Base", "Optimistic")):
        cell(d, f"{col}{i}", f"=Model!{outputs[sc][k]}", GREEN, fmt=fmt)
cell(d, "A13", "Investment (Rp B)", BOLD)
for col in "BCD":
    cell(d, f"{col}13", f"=Assumptions!{col}37", GREEN, fmt=RP)
cell(d, "A15", "Note: with pilot-light phasing the 2026 outflow is small, so IRR looks extreme. Lead with NPV and P(NPV>0) from the Simulation tab, not IRR.", BOLD)
cell(d, "A14", "Variant modification time (months, today 9)", BOLD)
for col in "BCD":
    cell(d, f"{col}14", f"=Assumptions!{col}40", GREEN, fmt="0.0")

header_row(d, 16, ["Base case savings by lever", "2026", "2027", "2028", "2029", "2030"])
br = outputs["Base"]["rows"]
for i, (lab, k) in enumerate([("Scrap", "scrap"), ("Maintenance", "maint"), ("Operator NVA", "labor"),
                               ("Energy", "energy"), ("Variant modification", "variant")], start=17):
    cell(d, f"A{i}", lab)
    for yc, col in zip(YC, "BCDEF"):
        cell(d, f"{col}{i}", f"=Model!{yc}{br[k]}", GREEN, fmt=RP)

ch = BarChart(); ch.type = "col"; ch.title = "NPV by scenario (Rp B)"
ch.add_data(Reference(d, min_col=2, max_col=4, min_row=4, max_row=4), from_rows=True, titles_from_data=False)
ch.set_categories(Reference(d, min_col=2, max_col=4, min_row=3, max_row=3))
ch.legend = None; ch.height = 7; ch.width = 13
d.add_chart(ch, "G3")
ch2 = BarChart(); ch2.type = "col"; ch2.grouping = "stacked"; ch2.overlap = 100
ch2.title = "Base case savings by lever (Rp B)"
ch2.add_data(Reference(d, min_col=1, max_col=6, min_row=17, max_row=21), from_rows=True, titles_from_data=True)
ch2.set_categories(Reference(d, min_col=2, max_col=6, min_row=16, max_row=16))
ch2.height = 8; ch2.width = 15
d.add_chart(ch2, "G18")
widths(d, {"A": 40, "B": 14, "C": 14, "D": 14, "E": 12, "F": 12})

# ------------------------------------------------------------------ BREAKEVEN
b = wb.create_sheet("Breakeven")
cell(b, "A1", "How much saving pays back the program?", TITLE)
cell(b, "A2", "Simplified: investment at start, steady savings from year 1 growing with escalation, no running cost.", BLACK)
cell(b, "A4", "Discount rate"); cell(b, "B4", "=Assumptions!B9", GREEN, fmt=PCT)
cell(b, "A5", "Savings growth (escalation)"); cell(b, "B5", "=Assumptions!B10", GREEN, fmt=PCT)
cell(b, "A6", "Years"); cell(b, "B6", "=Assumptions!B11", GREEN)
cell(b, "A7", "Growing annuity factor (PV of Rp1 first-year saving)", BOLD)
cell(b, "B7", "=(1-((1+B5)/(1+B4))^B6)/(B4-B5)", BOLD, fmt="0.000")
cell(b, "A8", "Annual conversion cost (Rp B)"); cell(b, "B8", "=Assumptions!B8", GREEN, fmt=RP)
header_row(b, 10, ["Investment (Rp B)", "Break-even first-year saving (Rp B)", "% of conversion cost", "Share of gap to benchmark that must close"])
for i, inv in enumerate([40, 60, 80, 100, 120], start=11):
    cell(b, f"A{i}", inv, BLUE, fmt=RP0)
    cell(b, f"B{i}", f"=A{i}/$B$7", fmt=RP)
    cell(b, f"C{i}", f"=B{i}/$B$8", fmt=PCT)
    cell(b, f"D{i}", f"=C{i}*Assumptions!$B$12/(Assumptions!$B$12-Assumptions!$B$13)", fmt=PCT)
cell(b, "A17", "Reading: if break-even needs only a small share of the gap closed, the case for investing is strong.", BLACK)
cell(b, "A19", "NPV sensitivity grid (simplified): rows = investment, columns = first-year savings (Rp B)", BOLD)
sav_vals = [10, 20, 30, 40, 50, 60]
cell(b, "A20", "Invest \\ Savings", H2, HFILL)
for j, s_ in enumerate(sav_vals):
    cell(b, f"{L(2+j)}20", s_, Font(name=F, bold=True, color="0000FF"), SUB, RP0)
for i, inv in enumerate([40, 60, 80, 100, 120], start=21):
    cell(b, f"A{i}", inv, Font(name=F, bold=True, color="0000FF"), SUB, RP0)
    for j in range(len(sav_vals)):
        col = L(2 + j)
        cell(b, f"{col}{i}", f"={col}$20*$B$7-$A{i}", fmt=RP, border=True)
widths(b, {"A": 46, "B": 22, "C": 18, "D": 26, "E": 12, "F": 12, "G": 12})

# ------------------------------------------------------------------ KPIs
k = wb.create_sheet("KPIs")
cell(k, "A1", "KPI tree: baseline from exhibits, targets are suggestions to debate", TITLE)
header_row(k, 3, ["Level", "KPI", "Baseline", "Pilot target (2027)", "Target 2030", "Source of baseline", "Why judges care"])
kp = [
    ("Outcome: cost", "Conversion cost index (2023=100)", 106, 102, "=Dashboard!C10", "Exhibit 3", "Headline competitiveness vs benchmark 89"),
    ("Outcome: quality", "Scrap index", 108, 95, 75, "Exhibit 4 (VERIFY)", "Direct cost + quality signal"),
    ("Outcome: quality", "Defects escaping downstream (index)", 103, 90, 60, "Exhibit 4 (VERIFY)", "Proves the closed loop works"),
    ("Outcome: flexibility", "Equipment modification time per variant (months)", 9, 7, "=Dashboard!C14", "Exhibit 4", "Multi-pathway readiness"),
    ("Driver: process", "Unplanned downtime (index)", 111, 100, 75, "Exhibit 4", "Maintenance shift to predictive"),
    ("Driver: process", "Operator NVA time (% hours)", 0.22, 0.19, 0.15, "Exhibit 4", "Productivity"),
    ("Driver: process", "Processes on common data/interface standard (%)", 0, 0.15, 0.80, "New KPI", "Measures integration, not gadgets"),
    ("Driver: people", "Engineer time on improvement (%)", 0.25, 0.30, "=Capability!G31", "Exhibit 6A", "Talent not wasted"),
    ("Driver: people", "Improvement ideas per engineer per year", 2.4, 3.0, "=Capability!G34", "Exhibit 6A", "Kaizen engine restarted"),
    ("Driver: people", "Ideas implemented (% submitted)", 0.28, 0.35, 0.50, "Exhibit 6A", "Ideas turn into value"),
    ("Driver: people", "Operators trained on data-driven tools (%)", 0.18, 0.50, 0.90, "Exhibit 6B", "Adoption"),
    ("Driver: people", "Operators overriding automated alerts (%)", 0.31, 0.20, 0.10, "Exhibit 6B", "Trust in the system"),
    ("Driver: knowledge", "Critical know-how documented & shared (%)", 0.33, 0.50, "=Capability!G35", "Exhibit 6A", "Knowledge no longer in 1-2 heads"),
    ("Driver: knowledge", "Months for new engineer to work independently", 15, 13, "=Capability!G36", "Exhibit 6A", "Knowledge transfer speed"),
    ("Driver: capability", "Engineers at Software & AI level 3+ (of 30)", 2, 6, "=Capability!B39", "Exhibit 7", "In-house capability built"),
    ("Driver: capability", "Engineers at Programming level 3+ (of 30)", 6, 10, "=Capability!B40", "Exhibit 7", "In-house capability built"),
]
for i, row in enumerate(kp, start=4):
    for j, v in enumerate(row):
        col = L(1 + j)
        is_f = isinstance(v, str) and str(v).startswith("=")
        font = GREEN if is_f else (BLUE if j in (2, 3, 4) else (BOLD if j == 0 else BLACK))
        fill = RED if v == "VERIFY" else None
        pct_row = j in (2, 3, 4) and any(isinstance(x, float) and x <= 1 for x in row[2:5])
        fmt = PCT if pct_row else ("0.0" if is_f else None)
        c = cell(k, f"{col}{i}", v, font, fill, fmt, wrap=j in (1, 5, 6), border=True)
widths(k, {"A": 18, "B": 44, "C": 11, "D": 15, "E": 12, "F": 22, "G": 36})
k.freeze_panes = "C4"

# ------------------------------------------------------------------ IDEATION
idx = wb.create_sheet("Ideation")
cell(idx, "A1", "Idea options: generate, compare, then combine into ONE system", TITLE)
cell(idx, "A2", "Case rule: the answer must change HOW manufacturing works (process, ways of working, people, knowledge), not recommend a product or machine.", BOLD)
ideas = [
    ("A", "Closed-Loop Jidoka (\"Self-Healing Line\")",
     "Every abnormality detected anywhere (AI inspection, sensors, operator) is routed automatically to the upstream process that caused it, with a clear stop / correct / escalate rule. Operators confirm and fix; the line learns.",
     "Inspection L1, sealer with no feedback, defects found late, scrap up, 31% override alerts",
     "Jidoka, andon, built-in quality",
     "Toyota Japan uses worker-built AI models for adhesive-application inspection",
     "Strong cost + quality story; uses the Oct 2026 AI camera as a building block",
     "Needs data integration first; alert fatigue if poorly designed"),
    ("B", "Plug-and-Produce Plant Standard (in-house)",
     "TMMIN defines one common interface + data standard; every new or modified equipment plugs into it. In-house engineers build standard equipment and apps on top. Variant change becomes configuration, not rewiring.",
     "Point-to-point integration, 9-month modification, scattered data, costly closed external tech",
     "Standardized work applied to equipment; heijunka for mixed models",
     "Toyota insources equipment tech (self-propelled conveyance at Motomachi)",
     "Direct answer to multi-pathway flexibility and in-house capability",
     "Less emotional / people story on its own; standard-setting takes discipline"),
    ("C", "Citizen Kaizen AI Platform",
     "Team leaders and operators build simple AI / data tools themselves through a no-code platform, plus an easy idea channel with fast engineer support. Engineers become coaches and platform owners.",
     "Ideas down 3.1->2.4, implementation 35%->28%, 62% would contribute with an easy channel, 18% trained",
     "Kaizen, respect for people",
     "Toyota AI Platform: ~10,000 models built by factory staff, ~1,200 active users",
     "Most human-centered; scales kaizen; very Toyota",
     "Needs governance (model quality, safety); training load"),
    ("D", "Shop-Floor O-Beya (\"Digital Sensei\")",
     "Capture senior experts' troubleshooting and process know-how into shared standards and an AI assistant that new engineers and team leaders consult. Experts validate content; it becomes living standard work.",
     "Know-how with 1-2 seniors, low documentation, 15-month ramp-up, engineers stuck firefighting",
     "Yokoten (horizontal deployment), standardized work, hansei",
     "Toyota O-Beya: 9 AI agents for ~800 powertrain engineers",
     "Cheap, fast to pilot, addresses knowledge and talent directly",
     "Weaker direct cost impact; content quality depends on seniors' time"),
    ("E", "Simulation-First Production Preparation",
     "Every new variant / pathway is designed, balanced and debugged in a digital model of the line before physical change. Engineers own the models.",
     "9-month modification, multi-pathway mix uncertainty (Exhibit 8)",
     "Genchi genbutsu supported by virtual verification; PDCA",
     "Toyota digital process verification for next-gen BEV plants (aim: halve prep lead time)",
     "Strong flexibility + time-to-market story; fits IE skills",
     "Needs reliable data; model upkeep cost"),
    ("F", "Conveyor-Light Flexible Line + Synchronized Intralogistics",
     "Redesign flow around mobile automation (AMR/AGV, self-propelled concepts) so layout and sequence adapt to the variant mix; material flow synced with production signals.",
     "Manual forklifts/dollies, flow not synchronized, NVA 22%",
     "JIT, kanban, heijunka",
     "Toyota self-propelled assembly line trials",
     "Big flexibility upside, visually impressive",
     "Capex heavy, risks reading as equipment recommendation"),
    ("G", "AI-Enabled Autonomous Maintenance (TPM 2.0)",
     "Operators and maintenance jointly own equipment health using condition data; predictive alerts with operator-led first response.",
     "Periodic preventive only, rising unplanned downtime",
     "TPM, jidoka",
     "Toyota AI Platform used for injection-moulding abnormality detection",
     "Clear downtime savings, practical",
     "Narrower scope; many competitors will propose it"),
    ("H", "INTEGRATED: Closed-Loop Production System (A+B+C+D)",
     "One operating system with three loops: quality loop (A), data/equipment loop (B), people & knowledge loop (C+D). Piloted in one area, standardized, then rolled out plant-wide.",
     "Attacks all three complications at once",
     "Jidoka + kaizen + standardization, in the digital era",
     "Combines the Toyota precedents above",
     "Best answer to 'system not product'; one memorable idea",
     "Complex to explain: needs one clean diagram and one pilot"),
]
GC = "Google Cloud (2024) Toyota AI Platform: https://cloud.google.com/blog/topics/hybrid-cloud/toyota-ai-platform-manufacturing-efficiency"
CAIO = "Chief AI Officer (2025) 10,000 models / 10,000 hrs: https://chiefaiofficer.com/blog/how-toyota-gave-ai-tools-to-factory-workers-and-saved-10000-hours/"
MS = "Microsoft Source Asia (2024) O-Beya: https://news.microsoft.com/source/asia/features/toyota-is-deploying-ai-agents-to-harness-the-collective-wisdom-of-engineers-and-innovate-faster/"
ABI = "ABI Research (2025) O-Beya knowledge mgmt: https://www.abiresearch.com/market-research/insight/7786905-toyotas-o-beya-provides-best-practices-for"
AIC = "Aicadium (2026) Lean to AI, GAIA + 100-course academy: https://aicadium.ai/lean-to-ai-what-toyotas-transformation-looks-like-today/"
T1 = "Toyota (2023) BEV production process, halve prep lead time & investment: https://global.toyota/en/newsroom/corporate/39330500.html"
T2 = "Toyota (2023) Monozukuri tech, in-house self-propelled conveyance: https://global.toyota/en/newsroom/corporate/39758451.html"
FF = "The Future Factory (2026) TPS in the age of AI: https://www.thefuturefactory.com/insights/toyota-production-system-age-of-ai"
DD = "DigitalDefynd (2026) 10 ways Toyota uses AI: https://digitaldefynd.com/IQ/toyota-using-ai-case-study/"
AM = "Assembly Magazine (2023) self-propelled lines: https://www.assemblymag.com/articles/98199-toyota-outlines-future-production-processes"
LV = "Logistics Viewpoints (2025) People + AI: https://logisticsviewpoints.com/2025/06/05/people-ai-augmenting-the-supply-chain-workforce/"
SIM = "Own test: Simulation tab (closed-loop quality sim + Monte Carlo)"
refs = {
    "A": [GC, DD, FF, SIM],
    "B": [T2, T1, "Case: point-to-point integration, 9-month modification (Exhibits 4, 5)"],
    "C": [GC, CAIO, "Case Exhibit 6B: 62% would contribute ideas with an easy channel"],
    "D": [MS, ABI, AIC, "Case Exhibit 6A: know-how with 1-2 seniors, 15-month ramp-up"],
    "E": [T1, "Case Exhibit 8: electrified share 30% -> 55-70%"],
    "F": [AM, T2],
    "G": [GC, LV],
    "H": [GC, MS, T2, AIC, SIM],
}
r0 = 4
r_end = text_table(idx, r0, ["#", "Idea", "How manufacturing changes", "Case gaps it closes", "TPS anchor", "Public Toyota precedent", "Strength", "Risk / weakness", "References & evidence (cite in deck)"],
                   [(i[0],) + i[1:] + ("\n".join(refs[i[0]]),) for i in ideas], height=150)
widths(idx, {"A": 6, "B": 28, "C": 52, "D": 36, "E": 22, "F": 32, "G": 30, "H": 30, "I": 60})

sr = r_end + 2
cell(idx, f"A{sr}", "Scoring matrix (scores 1-5 are suggestions: re-score as a team on Day 3)", BOLD)
crit = [("Cost & quality impact", 0.25), ("Multi-pathway flexibility", 0.15), ("People at the center / knowledge", 0.20),
        ("Hard to buy off the shelf (in-house value)", 0.15), ("Feasible in Rp40-120B by 2030", 0.15), ("Fits case ask: system, not product", 0.10)]
header_row(idx, sr + 1, ["#", "Idea"] + [c[0] for c in crit] + ["Weighted score", "Rank"])
cell(idx, f"B{sr+2}", "Weight", BOLD)
for j, (_, w) in enumerate(crit):
    cell(idx, f"{L(3+j)}{sr+2}", w, BLUE, YEL, PCT)
cell(idx, f"I{sr+2}", f"=SUM(C{sr+2}:H{sr+2})", BOLD, fmt=PCT)
scores = {"A": (5, 3, 4, 4, 4, 5), "B": (3, 5, 3, 5, 3, 5), "C": (4, 3, 5, 5, 4, 4), "D": (2, 3, 5, 4, 5, 4),
          "E": (3, 5, 3, 4, 4, 4), "F": (3, 5, 2, 2, 2, 2), "G": (4, 2, 4, 3, 4, 3), "H": (5, 4, 5, 5, 3, 5)}
first = sr + 3
for n, ide in enumerate(ideas):
    rr = first + n
    cell(idx, f"A{rr}", ide[0], BOLD); cell(idx, f"B{rr}", ide[1], wrap=True)
    for j, v in enumerate(scores[ide[0]]):
        cell(idx, f"{L(3+j)}{rr}", v, BLUE, border=True)
    cell(idx, f"I{rr}", f"=SUMPRODUCT($C${sr+2}:$H${sr+2},C{rr}:H{rr})", BOLD, fmt="0.00")
last = first + len(ideas) - 1
for n in range(len(ideas)):
    rr = first + n
    cell(idx, f"J{rr}", f"=RANK(I{rr},$I${first}:$I${last})")
cell(idx, f"A{last+2}", "Tip: the winning pitch is usually one integrated idea (like H) explained through one pilot. Use the lower-ranked options as 'considered and rejected' in the appendix to show rigor.", BOLD)
idx.column_dimensions["J"].width = 10

# ------------------------------------------------------------------ ANSWER GUIDE
g = wb.create_sheet("Answer_Guide")
cell(g, "A1", "How to answer each sub-question", TITLE)
guide = [
    ("Executive summary (1 slide)",
     "One clear answer in 30 seconds: the idea, why now, impact, investment, ask.",
     "Write it LAST but draft it on Day 3. Situation (cost index 106 vs 89, multi-pathway coming) -> Complication (open loops in quality, data, knowledge) -> Answer (your one system) -> Impact (NPV, index, months) -> Roadmap headline.",
     "Exhibit 3, Dashboard", "Dashboard",
     "Listing 5 ideas; burying the number; no single name for the idea."),
    ("SQ1. Future manufacturing vision & biggest gaps",
     "A vivid 2030 picture that goes BEYOND lower cost, and a prioritized, evidence-based gap.",
     "1) Write a 2030 vision statement (people + technology + flexibility). 2) Define 'new value' beyond cost: speed to launch variants, knowledge that compounds, engaged people. 3) Build a gap heat map: process (Exhibit 5) x impact on cost & quality (Exhibit 4). 4) Show the gap is BETWEEN processes (integration, data, feedback). 5) Pick 1-2 priority gaps.",
     "Exhibits 3, 4, 5, 8", "Exhibits",
     "Vision that is just a list of technologies; ignoring that the case says the gap lies between processes."),
    ("SQ2. Transformative idea",
     "How manufacturing itself changes; people stay at the center; mindset shift; know-how becomes shared knowledge.",
     "1) Name the idea and show ONE system diagram. 2) Walk through a 'day in the life' of an operator and an engineer before vs after. 3) Explain the mindset shift (operate & maintain -> improve & transform) and the mechanism that drives it (time freed, idea channel, recognition). 4) Show how know-how is captured, validated, reused. 5) Explain in-house vs partner logic. 6) Anchor every element in a TPS principle.",
     "Exhibits 6A, 6B, 7; Ideation tab", "Ideation",
     "Recommending a product/device; AI replacing people; no answer to the 31% who override alerts."),
    ("SQ3. Roadmap & capability building",
     "Credible phasing 2026-2030 with pilot, standardization, rollout, talent, partners, risks.",
     "1) Phase 0 (Q4 2026): build on AI camera validation; choose pilot area; set data standard. 2) Pilot (2027) with go/no-go KPIs. 3) Standardize (2028). 4) Roll out (2029-30). 5) Talent: tiered academy moving engineers up Exhibit 7 levels, operator data training. 6) Partners only where they add distinctive value. 7) Risk register with mitigations.",
     "Exhibits 5, 6A, 7; Roadmap tab", "Roadmap, KPIs",
     "Everything starting in year 1; no gate criteria; no owner; ignoring training (18% trained)."),
    ("SQ4. Competitive & financial impact",
     "Impact on cost, quality, time, flexibility, capability; investment; KPIs. Numbers must be traceable.",
     "1) Bottom-up savings by lever (Model tab). 2) Investment inside Rp40-120B. 3) NPV at 10%, payback, IRR, 3 scenarios. 4) Break-even framing (Breakeven tab). 5) Translate to cost index vs benchmark. 6) Non-financial impact: months per variant, ramp-up time, ideas, skills. 7) KPI tree with baselines and targets.",
     "Exhibit 9, 3, 4; Model, Dashboard, Breakeven, KPIs", "Model, Dashboard",
     "Claiming 100% of the gap; ignoring running and training cost; no sensitivity; unlabeled assumptions."),
    ("Q&A preparation",
     "Calm, data-backed answers; shows the team owns the logic.",
     "Prepare answers for: Why this pilot area? What if operators resist? Why in-house, not buy? What if the AI camera fails validation? How do you avoid job losses? What happens in the aggressive BEV scenario? Which assumption hurts NPV most? How does this differ from what Toyota Japan already does?",
     "All", "Breakeven (sensitivity)",
     "One person answering everything; arguing with judges."),
]
r_end = text_table(g, 3, ["Section", "What judges look for", "How to answer (steps)", "Data to use", "Model tab", "Traps to avoid"], guide, height=150)

sr = r_end + 2
cell(g, f"A{sr}", "Suggested deck storyline (fill [ ] with your numbers; titles must read as a story on their own)", BOLD)
story = [
    ("1", "Title", "Idea name + one-line promise"),
    ("2", "Executive summary", "TMMIN can close [x]% of its cost gap and cut variant changeover from 9 to [x] months by making the plant learn from itself"),
    ("3", "Situation", "Market fell 7% while new players run [~19]% cheaper per unit"),
    ("4", "Complication", "Multi-pathway mix lifts electrified share to [55-70]% by 2030, but every variant still costs ~9 months of rework"),
    ("5", "Root cause", "The real gap sits between processes: quality, data and know-how loops are open"),
    ("6", "2030 vision (SQ1)", "In 2030 TMMIN's advantage is a production system that learns, not one that is bought"),
    ("7", "Gap prioritization (SQ1)", "[Pilot area] is where the open loops cost the most"),
    ("8", "The idea (SQ2)", "[Idea name]: three closed loops with people at the center"),
    ("9", "How it works (SQ2)", "A day in the life: operator and engineer before vs after"),
    ("10", "Mindset & knowledge (SQ2)", "Engineers move from firefighting to improving, and know-how leaves the heads of a few experts"),
    ("11", "In-house vs partners (SQ2/3)", "Build what differentiates, partner where partners add distinctive value"),
    ("12", "Roadmap (SQ3)", "Pilot in 2027, standardize in 2028, plant-wide by 2030 with clear gates"),
    ("13", "Capability building (SQ3)", "[x] engineers reach Software & AI level 3+ by 2030 through a tiered academy"),
    ("14", "Financials (SQ4)", "Rp[x]B investment returns NPV of Rp[x]B; break-even needs only [x]% of the gap closed"),
    ("15", "KPIs (SQ4)", "[x] KPIs track outcomes and the people/knowledge drivers behind them"),
    ("16", "Risks", "Main risks are adoption and data quality, and each has a mitigation and an owner"),
    ("17", "Close", "Recap + the decision you want TMMIN to take now"),
    ("App.", "Appendix", "Assumptions list, sensitivity, alternatives considered (Ideation), exhibit re-type, methodology"),
]
owners = {"1": "M1", "2": "M1", "3": "M1", "4": "M1", "5": "M2", "6": "M1", "7": "M2", "8": "M2", "9": "M2", "10": "M1",
          "11": "M2", "12": "M2", "13": "M3", "14": "M3", "15": "M3", "16": "M1", "17": "M1", "App.": "M3"}
text_table(g, sr + 1, ["#", "Slide", "Example action title / content", "Owner"], [st + (owners[st[0]],) for st in story])
widths(g, {"A": 26, "B": 30, "C": 70, "D": 26, "E": 18, "F": 34})

# ------------------------------------------------------------------ ROADMAP
rm = wb.create_sheet("Roadmap")
cell(rm, "A1", "Roadmap template 2026-2030 (edit to match your chosen idea)", TITLE)
rmap = [
    ("Phase", "0. Prepare (Q4 2026)", "1. Pilot", "2. Standardize", "3. Roll out", "4. Scale & sustain"),
    ("Quick wins (protect the ramp-up)", "Sealer closed loop on existing CCTV AI camera after Oct 2026 validation; digital andon for alerts; idea channel live", "First citizen-built tools in pilot; top-20 troubleshooting know-how captured; monthly savings tracked vs plan", "Copy proven quick wins to 2-3 areas", "Quick-win playbook in standard work", "Continuous kaizen pipeline"),
    ("Process & quality loop", "Map pilot area value stream; define stop/correct rules; baseline KPIs", "Closed-loop feedback live in pilot area (e.g. sealer -> inspection)", "Standard loop design + yokoten to 2-3 areas", "All vehicle processes Karawang I & II", "Extend to engine plants (Sunter, Karawang III)"),
    ("Data & equipment standard", "Draft common interface/data standard; inventory equipment generations", "Pilot area on the standard", "Standard mandatory for new/modified equipment", "Legacy retrofit by priority", "Variant change by configuration"),
    ("People & kaizen", "Idea channel launched; change champions per line", "Operators in pilot trained; first citizen-built tools", "Kaizen + data skills in standard training", "Plant-wide adoption; recognition system", "Self-sustaining improvement culture"),
    ("Knowledge", "Identify critical know-how held by 1-2 seniors", "Capture & validate top items for pilot area", "Knowledge base linked to standard work", "All critical processes covered", "Living knowledge updated through kaizen"),
    ("Capability (Exhibit 7)", "Skills assessment; academy design", "Cohort 1 (Software & AI L1 -> L2)", "Cohort 2 + first L3 engineers", "Internal trainers from L3 engineers", "Target L3+ count reached"),
    ("Technology building blocks", "AI camera validation completes (Oct 2026)", "Use validated building blocks in pilot", "Reusable components library", "Scale infrastructure", "Continuous upgrade"),
    ("Partners", "Decide build vs partner per component", "Partners for distinctive tech only", "Knowledge transfer clauses", "Reduce dependency", "Strategic partnerships"),
    ("Gate / go-no-go", "Pilot area + KPIs agreed", "Pilot KPIs met?", "Standard proven in 2+ areas?", "Rollout on budget?", "2030 targets met"),
    ("Investment share", "=Assumptions!B44", "=Assumptions!C44", "=Assumptions!D44", "=Assumptions!E44", "=Assumptions!F44"),
]
header_row(rm, 3, list(rmap[0]))
for i, row in enumerate(rmap[1:], start=4):
    for j, v in enumerate(row):
        is_f = isinstance(v, str) and v.startswith("=")
        cell(rm, f"{L(1+j)}{i}", v, GREEN if is_f else (BOLD if j == 0 else BLACK),
             fmt=PCT if is_f else None, wrap=True, border=True)
    rm.row_dimensions[i].height = 48
cell(rm, "A15", "Years per phase: align to Assumptions timing row (2026 = prepare/pilot start, 2027 pilot, 2028 standardize, 2029 rollout, 2030 scale).", BOLD)
cell(rm, "A16", "Why quick wins matter: Simulation Test 2b, F: if savings arrive one year late, P(NPV>0) falls from ~85% to ~33%.", BOLD)
widths(rm, {"A": 26, "B": 30, "C": 30, "D": 30, "E": 30, "F": 30})

# ------------------------------------------------------------------ CAPABILITY (people model)
cp = wb.create_sheet("Capability")
cell(cp, "A1", "Workforce capability & engineer time model (SQ3 / SQ4 workforce impact)", TITLE)
cell(cp, "A2", "Formulas only. Starting points from Exhibits 6A and 7; yellow cells are academy / knowledge assumptions to defend.", BLACK)
header_row(cp, 4, ["Academy assumption", "Value", "Note"])
capa = [(5, "Promotion rate L1 -> L2 per year", 0.30, "Share of L1 engineers reaching L2 each year via academy cohort"),
        (6, "Promotion rate L2 -> L3 per year", 0.20, "Needs project-based learning in the pilot"),
        (7, "Promotion rate L3 -> L4 per year", 0.10, "Expert level; partner / university collaboration"),
        (8, "Annual cut in routine-support share (pct points)", 0.04, "From knowledge base + citizen tools absorbing troubleshooting"),
        (9, "Floor for routine-support share", 0.45, "Some routine work always remains"),
        (10, "Engineer working hours per year", 1800, "Per engineer"),
        (11, "Engineers in production engineering team", 30, "Exhibit 7: N = 30 per field"),
        (12, "Annual rise in critical know-how documented (pct points)", 0.10, "Knowledge capture sprints with seniors"),
        (13, "Ramp-up months saved per +10 pts documented know-how", 1.2, "Assumption: tested in pilot cohort")]
for row, lab, v, note in capa:
    cell(cp, f"A{row}", lab); cell(cp, f"B{row}", v, BLUE, YEL, PCT if isinstance(v, float) and v < 1 else None)
    cell(cp, f"C{row}", note)
yrs = ["2025", "2026", "2027", "2028", "2029", "2030"]
YC6 = ["B", "C", "D", "E", "F", "G"]


def level_block(start, title, base):
    header_row(cp, start, [title] + yrs)
    labs = ["Level 1 basic", "Level 2 intermediate", "Level 3 proficient", "Level 4 expert", "Engineers at L3+"]
    for i, lab in enumerate(labs):
        cell(cp, f"A{start+1+i}", lab, BOLD if i == 4 else BLACK)
    for i, v in enumerate(base):
        cell(cp, f"B{start+1+i}", v, BLUE, fmt="0.0")
    r1, r2, r3, r4 = start + 1, start + 2, start + 3, start + 4
    for prev, col in zip(YC6[:-1], YC6[1:]):
        cell(cp, f"{col}{r1}", f"={prev}{r1}*(1-$B$5)", fmt="0.0")
        cell(cp, f"{col}{r2}", f"={prev}{r2}*(1-$B$6)+{prev}{r1}*$B$5", fmt="0.0")
        cell(cp, f"{col}{r3}", f"={prev}{r3}*(1-$B$7)+{prev}{r2}*$B$6", fmt="0.0")
        cell(cp, f"{col}{r4}", f"={prev}{r4}+{prev}{r3}*$B$7", fmt="0.0")
    for col in YC6:
        cell(cp, f"{col}{start+5}", f"={col}{r3}+{col}{r4}", BOLD, fmt="0.0")
    return start + 5


sw_l3 = level_block(15, "Software & AI (members per level)", (20, 8, 2, 0))
pg_l3 = level_block(22, "Programming (members per level)", (14, 10, 5, 1))
header_row(cp, 29, ["Engineer time & knowledge"] + yrs)
tl = [(30, "Routine support share", 0.65, PCT), (31, "Improvement & development share", None, PCT),
      (32, "Improvement hours (team / yr)", None, RP0), (33, "Extra improvement hours vs 2025", None, RP0),
      (34, "Ideas per engineer (scales with improvement time)", 2.4, "0.0"),
      (35, "Critical know-how documented", 0.33, PCT), (36, "Months for new engineer to work independently", 15, "0.0")]
for row, lab, base_v, fmt in tl:
    cell(cp, f"A{row}", lab)
    if base_v is not None:
        cell(cp, f"B{row}", base_v, BLUE, fmt=fmt)
for col_i, col in enumerate(YC6):
    prev = YC6[col_i - 1] if col_i else None
    if prev:
        cell(cp, f"{col}30", f"=MAX($B$9,{prev}30-$B$8)", fmt=PCT)
        cell(cp, f"{col}34", f"=$B$34*{col}31/$B$31", fmt="0.0")
        cell(cp, f"{col}35", f"=MIN(0.95,{prev}35+$B$12)", fmt=PCT)
        cell(cp, f"{col}36", f"=MAX(6,$B$36-({col}35-$B$35)*10*$B$13)", fmt="0.0")
    cell(cp, f"{col}31", f"=0.25+($B$30-{col}30)", fmt=PCT)
    cell(cp, f"{col}32", f"={col}31*$B$10*$B$11", fmt=RP0)
    cell(cp, f"{col}33", f"={col}32-$B$32", fmt=RP0)
cell(cp, "A38", "Compare with KPI targets", BOLD)
cell(cp, "A39", "Software & AI engineers at L3+ in 2030 (feeds KPIs tab)"); cell(cp, "B39", f"=G{sw_l3}", BOLD, fmt="0.0")
cell(cp, "A40", "Programming engineers at L3+ in 2030 (feeds KPIs tab)"); cell(cp, "B40", f"=G{pg_l3}", BOLD, fmt="0.0")
cell(cp, "A41", "Engineer improvement share 2030 (feeds KPIs tab)"); cell(cp, "B41", "=G31", BOLD, fmt=PCT)
cell(cp, "A42", "Extra improvement hours per year by 2030"); cell(cp, "B42", "=G33", BOLD, fmt=RP0)
cell(cp, "A43", "Reading: if the model misses a KPI target, either the target or the academy design must change. Keep the two consistent in the deck.", BLACK)
widths(cp, {"A": 52, "B": 13, "C": 13, "D": 13, "E": 13, "F": 13, "G": 13})

# ------------------------------------------------------------------ RISKS
rk = wb.create_sheet("Risks")
cell(rk, "A1", "Risk register (score = likelihood x impact, 1-5 each)", TITLE)
header_row(rk, 3, ["Risk", "Likelihood", "Impact", "Score", "Mitigation built into the idea", "Early-warning KPI", "Evidence / test", "Owner"])
risks = [
    ("Operators distrust or override AI alerts", 4, 5, "Co-design alerts with team leaders; explain-why alerts; training before go-live; override reasons logged as kaizen input", "Alert override rate (31% today)", "Simulation: dismissals at 31% cut the scrap gain from ~85% to ~65%", "People lead"),
    ("Pilot adoption below plan", 3, 5, "Pilot-light phasing; go/no-go gate end-2027 on adoption + scrap KPIs", "Adoption %, pilot KPI hit rate", "Simulation Test 2b: gate + pilot-light raises P(NPV>0)", "Program lead"),
    ("AI camera fails accuracy/durability validation (Oct 2026)", 2, 4, "Loop design is sensor-agnostic; fall back to operator check + digital andon while model is retrained", "Validation accuracy vs threshold", "Case: validation target Oct 2026", "Engineering"),
    ("Data integration harder than expected (legacy equipment)", 4, 4, "Start with pilot area only; common interface standard for new equipment first; retrofit by priority", "% pilot equipment on standard", "Exhibit 5: no common interface today", "Engineering"),
    ("Engineers lack software/AI skills to build in-house", 4, 4, "Academy cohorts; partner for first build with knowledge-transfer clause", "Engineers at L3+ (Capability tab)", "Exhibit 7: 2 of 30 at L3+ in Software & AI", "People lead"),
    ("Senior experts lack time to capture know-how", 3, 3, "Protected capture sprints; recognition; AI-assisted interview transcripts validated by experts", "% critical know-how documented", "Exhibit 6A", "Knowledge lead"),
    ("Savings not converted to cash (freed time absorbed)", 3, 3, "Redeploy freed time to kaizen with tracked outcomes; no-layoff pledge to protect trust", "Hours redeployed vs ideas implemented", "Assumptions: 50% cash realization", "Finance"),
    ("Savings ramp slower than plan (pilot results arrive late)", 3, 5, "Start Phase 0 now on existing CCTV camera; pick quick wins for 2026-27; weekly pilot KPI review", "Pilot savings vs plan each quarter", "Simulation Test 2b, F: one-year delay cuts P(NPV>0) from ~85% to ~33%", "Program lead"),
    ("BEV volume ramps faster than plan (aggressive scenario)", 2, 4, "Plug-and-produce standard lowers variant change cost; simulation-first preparation", "Months per variant change", "Exhibit 8 aggressive scenario: BEV 20% by 2030", "Program lead"),
    ("Cybersecurity / data-governance issue from connected equipment", 2, 4, "Segmented plant network; access governance in the data standard", "Security incidents", "Team judgement", "IT"),
]
for i, (rsk, lk, im, mit, kpi, ev, own) in enumerate(risks, start=4):
    cell(rk, f"A{i}", rsk, BOLD, wrap=True, border=True)
    cell(rk, f"B{i}", lk, BLUE, border=True); cell(rk, f"C{i}", im, BLUE, border=True)
    cell(rk, f"D{i}", f"=B{i}*C{i}", BOLD, border=True)
    for col, v in zip("EFGH", (mit, kpi, ev, own)):
        cell(rk, f"{col}{i}", v, wrap=True, border=True)
    rk.row_dimensions[i].height = 48
from openpyxl.formatting.rule import CellIsRule, FormulaRule
rk.conditional_formatting.add(f"D4:D{3+len(risks)}", CellIsRule(operator="greaterThanOrEqual", formula=["15"], fill=RED))
rk.conditional_formatting.add(f"D4:D{3+len(risks)}", CellIsRule(operator="between", formula=["8", "14"], fill=YEL))
widths(rk, {"A": 36, "B": 11, "C": 9, "D": 8, "E": 48, "F": 26, "G": 36, "H": 15})

# ------------------------------------------------------------------ WBS
wbs = wb.create_sheet("WBS")
cell(wbs, "A1", "Work breakdown structure: 7 days, 3 members", TITLE)
cell(wbs, "A2", "Type your names in the yellow cells. Owner = accountable (hours counted); Support = helps. Update Status daily in the stand-up. Daily load is red above 6.5 hours.", BLACK)
members = [("M1", "Lead, storyline & people", "Owns problem framing, vision, idea decision, mindset & knowledge mechanism, governance, risks, exec summary, speaking script, mocks, submission"),
           ("M2", "Operations, TPS & roadmap", "Owns gap heat map, root cause, system diagram, day-in-the-life, build-vs-partner, TPS fit, roadmap, slide template and design polish"),
           ("M3", "Quant, finance & evidence", "Owns exhibits data, benchmarks, assumptions, Model, simulation re-runs, capability model, KPIs, appendix, number tie-out, Q&A bank")]
header_row(wbs, 4, ["Code", "Name", "Role & accountable for", "Hours owned", "Tasks owned", "Tasks done", "", "", "", "Load (h/day)",
                     "D1", "D2", "D3", "D4", "D5", "D6", "D7"])
for i, (code, role, desc) in enumerate(members, start=5):
    cell(wbs, f"A{i}", code, BOLD)
    cell(wbs, f"B{i}", f"[Name {code}]", BLUE, YEL)
    cell(wbs, f"C{i}", f"{role}: {desc}", wrap=True)
    cell(wbs, f"D{i}", f"=SUMIF($D$13:$D$70,A{i},$H$13:$H$70)", BOLD, fmt="0")
    cell(wbs, f"E{i}", f"=COUNTIF($D$13:$D$70,A{i})")
    cell(wbs, f"F{i}", f'=COUNTIFS($D$13:$D$70,A{i},$J$13:$J$70,"Done")')
    cell(wbs, f"J{i}", code, BOLD)
    for di, col in enumerate("KLMNOPQ", start=1):
        cell(wbs, f"{col}{i}", f"=SUMPRODUCT(($D$13:$D$70=$A{i})*($F$13:$F$70<={di})*($G$13:$G$70>={di}),$H$13:$H$70/($G$13:$G$70-$F$13:$F$70+1))", fmt="0.0")
    for col in "ABCDEFJKLMNOPQ":
        wbs[f"{col}{i}"].alignment = Alignment(wrap_text=True, vertical="top")
    wbs.row_dimensions[i].height = 54
cell(wbs, "A8", "Total", BOLD); cell(wbs, "D8", "=SUM(D5:D7)", BOLD, fmt="0"); cell(wbs, "E8", "=SUM(E5:E7)", BOLD)
cell(wbs, "F8", "=SUM(F5:F7)", BOLD)
cell(wbs, "J8", "Team", BOLD)
for col in "KLMNOPQ":
    cell(wbs, f"{col}8", f"=SUM({col}5:{col}7)", BOLD, fmt="0.0")
wbs.conditional_formatting.add("K5:Q7", CellIsRule(operator="greaterThan", formula=["6.5"], fill=RED))
wbs.conditional_formatting.add("K5:Q7", CellIsRule(operator="between", formula=["5", "6.5"], fill=YEL))
cell(wbs, "C9", "Owned hours are balanced within ~4 h. Each member also supports others' tasks (Support column).", BLACK)
header_row(wbs, 12, ["WBS", "Work package / task", "Deliverable & done criteria", "Owner", "Support", "Start day", "End day", "Hours", "Depends on", "Status",
                     "D1", "D2", "D3", "D4", "D5", "D6", "D7"])
tasks = [
    ("1", "PROJECT MANAGEMENT", None),
    ("1.1", "Kick-off: roles, deadline, shared drive, task tracker", "Roles agreed, folder + tracker live", "M1", "All", 1, 1, 2, ""),
    ("1.2", "Confirm rules in writing (slide limit, format, AI use, judging criteria)", "Written confirmation saved", "M1", "", 1, 1, 1, ""),
    ("1.3", "Daily 15-min stand-up + update this sheet", "Status column current every evening", "M1", "All", 1, 7, 2, "1.1"),
    ("2", "DIAGNOSE THE PROBLEM (SQ1)", None),
    ("2.1", "Re-type exhibits from PDF; clear all red cells", "Exhibits tab has zero VERIFY cells", "M3", "M2", 1, 1, 2, ""),
    ("2.2", "Issue tree + problem statement", "1-page issue tree, MECE, agreed by team", "M1", "All", 1, 1, 3, "2.1"),
    ("2.3", "Gap heat map: process x cost/quality impact", "Heat map slide using Exhibits 4-5", "M2", "M3", 1, 2, 4, "2.1"),
    ("2.4", "Root cause (5-whys / fishbone) on the 3 complications", "Root-cause slide: 'open loops'", "M2", "M1", 2, 2, 3, "2.2"),
    ("2.5", "Benchmark research: Toyota precedents + lever benchmarks", "Ideation refs + Assumptions col G complete", "M3", "M2", 2, 3, 4, ""),
    ("2.6", "2030 vision + 'value beyond cost' statement", "Vision slide draft", "M1", "M2", 2, 2, 2, "2.3"),
    ("3", "DESIGN THE IDEA (SQ2)", None),
    ("3.1", "Ideation session: re-score 8 options as a team", "Scoring matrix updated with team scores", "M1", "All", 3, 3, 2, "2.4"),
    ("3.2", "Decide integrated idea + pilot area (decision log)", "One-line decision + 3 reasons", "M1", "All", 3, 3, 1, "3.1"),
    ("3.3", "System diagram: three closed loops", "One clean diagram, reviewed by all", "M2", "M1", 3, 3, 3, "3.2"),
    ("3.4", "Day-in-the-life before/after (operator, team leader, engineer)", "Before/after slide", "M2", "M1", 4, 4, 3, "3.2"),
    ("3.5", "Mindset & knowledge mechanism (idea channel, capture, recognition)", "Mechanism slide tied to Exhibits 6A/6B", "M1", "M2", 4, 4, 3, "3.2"),
    ("3.6", "Build vs partner logic per component", "2x2 or table slide", "M2", "M3", 4, 5, 2, "3.2"),
    ("3.7", "TPS principle mapping (jidoka, kaizen, standardized work, yokoten)", "Mapping table", "M2", "", 3, 3, 1, "3.3"),
    ("4", "ROADMAP & CAPABILITY (SQ3)", None),
    ("4.1", "Phased roadmap with gates (pilot-light)", "Roadmap slide with gate criteria", "M2", "M3", 4, 5, 3, "3.2"),
    ("4.2", "Capability plan using Capability tab", "Academy design + L3+ targets consistent with KPIs", "M3", "M1", 4, 5, 2, "3.2"),
    ("4.3", "Risk register + mitigations (quantify top risks with Simulation)", "Risks tab finalized, top 3 on slide", "M1", "M3", 5, 5, 2, "4.1"),
    ("4.4", "Governance: owners, cadence, partner roles", "Governance box on roadmap slide", "M1", "M2", 5, 5, 1, "4.1"),
    ("5", "IMPACT & FINANCIALS (SQ4)", None),
    ("5.1", "Defend every yellow assumption with a source or reason", "No yellow cell without a note", "M3", "M2", 3, 4, 4, "2.5"),
    ("5.2", "Update Model, scenarios, Dashboard", "Dashboard final; numbers frozen", "M3", "", 4, 4, 3, "5.1"),
    ("5.3", "Re-run run_tests.py with final assumptions", "Simulation tab refreshed", "M3", "", 5, 5, 2, "5.2"),
    ("5.4", "Finalize KPI tree (outcome + driver KPIs)", "KPI slide", "M3", "M2", 5, 6, 2, "5.2"),
    ("5.5", "Non-financial impact: time, flexibility, capability", "Impact summary slide", "M3", "M1", 5, 6, 2, "4.2"),
    ("6", "DECK & STORY", None),
    ("6.1", "Storyline skeleton with action titles", "Titles alone tell the story", "M1", "All", 3, 3, 2, "3.2"),
    ("6.2", "Slide template + visual system", "Master template shared", "M2", "", 2, 3, 2, ""),
    ("6.3", "SQ1 slides (situation, root cause, vision, gap)", "Draft slides", "M1", "M2", 4, 5, 3, "2.3"),
    ("6.4", "SQ2 slides (idea, mechanism, day-in-the-life)", "Draft slides", "M2", "M1", 5, 6, 4, "3.3"),
    ("6.5", "SQ3 slides (roadmap, capability, risks)", "Draft slides", "M2", "M3", 5, 6, 3, "4.1"),
    ("6.6", "SQ4 slides (financials, simulation, KPIs)", "Draft slides", "M3", "", 5, 6, 3, "5.2"),
    ("6.7", "Executive summary", "1 slide, readable in 30 seconds", "M1", "All", 6, 6, 2, "6.3"),
    ("6.8", "Appendix: assumptions, simulation, alternatives, sources", "Appendix complete, same style", "M3", "M2", 6, 6, 2, "5.3"),
    ("6.9", "Design polish + consistency pass", "One font, one color system, aligned charts", "M2", "", 6, 7, 3, "6.7"),
    ("7", "QUALITY & PRESENTATION", None),
    ("7.1", "Red-team review: each member attacks another's section", "Comment list closed", "M1", "All", 5, 6, 2, "6.3"),
    ("7.2", "Number tie-out: every number traced to tab/exhibit", "Checklist signed off", "M3", "M1", 6, 7, 2, "6.8"),
    ("7.3", "Q&A bank: answers + owner per question (QA_Bank tab)", "Every question has an owner + data point", "M3", "All", 7, 7, 2, "7.1"),
    ("7.4", "Speaker split + script (see split below)", "Each speaker has a 1-page script and handover lines", "M1", "All", 6, 6, 2, "6.7"),
    ("7.5", "Two timed mock presentations + Q&A drill", "Within time limit, smooth handovers", "M1", "All", 7, 7, 3, "7.4"),
    ("7.6", "Final proofread, export, submit early", "Submitted before deadline", "M1", "M2", 7, 7, 1, "7.5"),
]
r = 13
for t in tasks:
    if t[2] is None:
        cell(wbs, f"A{r}", t[0], BOLD, SUB); cell(wbs, f"B{r}", t[1], BOLD, SUB)
        for col in "CDEFGHIJKLMNOPQ":
            wbs[f"{col}{r}"].fill = SUB
        cell(wbs, f"F{r}", 0); cell(wbs, f"G{r}", 0); wbs[f"F{r}"].fill = SUB; wbs[f"G{r}"].fill = SUB
        wbs[f"F{r}"].font = Font(name=F, color="D9E1F2", size=10); wbs[f"G{r}"].font = Font(name=F, color="D9E1F2", size=10)
        r += 1; continue
    code, name, dlv, own, sup, s_, e_, hrs, dep = t
    cell(wbs, f"A{r}", code); cell(wbs, f"B{r}", name, wrap=True); cell(wbs, f"C{r}", dlv, wrap=True)
    cell(wbs, f"D{r}", own, BLUE); cell(wbs, f"E{r}", sup, BLUE)
    cell(wbs, f"F{r}", s_, BLUE); cell(wbs, f"G{r}", e_, BLUE); cell(wbs, f"H{r}", hrs, BLUE)
    cell(wbs, f"I{r}", dep); cell(wbs, f"J{r}", "Not started", BLUE, YEL)
    for di, col in enumerate("KLMNOPQ", start=1):
        cell(wbs, f"{col}{r}", f'=IF(AND({di}>=$F{r},{di}<=$G{r}),$D{r},"")')
    for col in "ABCDEFGHIJKLMNOPQ":
        wbs[f"{col}{r}"].alignment = Alignment(wrap_text=True, vertical="top")
    wbs.row_dimensions[r].height = 30
    r += 1
last_wbs = r - 1
for code, colr in (("M1", "BDD7EE"), ("M2", "C6E0B4"), ("M3", "FFE699")):
    wbs.conditional_formatting.add(f"K13:Q{last_wbs}", CellIsRule(operator="equal", formula=[f'"{code}"'], fill=PatternFill("solid", fgColor=colr)))
wbs.conditional_formatting.add(f"J13:J{last_wbs}", CellIsRule(operator="equal", formula=['"Done"'], fill=GRN))
from openpyxl.worksheet.datavalidation import DataValidation
dv = DataValidation(type="list", formula1='"Not started,In progress,Done,Blocked"', allow_blank=True)
wbs.add_data_validation(dv); dv.add(f"J13:J{last_wbs}")
rr = last_wbs + 2
cell(wbs, f"A{rr}", "Daily checkpoints (end of day)", BOLD); rr += 1
checks = ["D1: exhibits clean, issue tree agreed, rules confirmed", "D2: gap heat map, root cause, vision draft, benchmarks started",
          "D3: idea + pilot area LOCKED, system diagram, storyline skeleton", "D4: day-in-the-life, mechanism, model updated, roadmap draft",
          "D5: full draft deck, simulation re-run, red-team started", "D6: exec summary, appendix, speaker script, design pass",
          "D7: numbers tied out, Q&A drilled, two mocks, submit early"]
for c_ in checks:
    cell(wbs, f"B{rr}", c_); rr += 1
rr += 1
cell(wbs, f"A{rr}", "Speaker split (adjust % to the official time limit)", BOLD); rr += 1
header_row(wbs, rr, ["", "Section", "Speaker", "Share of time"]); rr += 1
spk = [("Opening, situation, root cause, 2030 vision (SQ1)", "M1", 0.25),
       ("The idea, how it works, day in the life, mindset & knowledge (SQ2)", "M2", 0.30),
       ("Roadmap, capability, risks (SQ3)", "M2", 0.10),
       ("Financial impact, simulation proof, KPIs (SQ4)", "M3", 0.25),
       ("Close and the decision we ask TMMIN to take", "M1", 0.10)]
sp0 = rr
for sec, who, share in spk:
    cell(wbs, f"B{rr}", sec, wrap=True); cell(wbs, f"C{rr}", who, BLUE); cell(wbs, f"D{rr}", share, BLUE, fmt=PCT); rr += 1
cell(wbs, f"B{rr}", "Check (must be 100%)", BOLD); cell(wbs, f"D{rr}", f"=SUM(D{sp0}:D{rr-1})", BOLD, fmt=PCT); rr += 1
cell(wbs, f"B{rr}", "Q&A rule: the owner of the slide answers first; the lead routes questions and closes. Never two people talking at once.", BLACK)
widths(wbs, {"A": 7, "B": 46, "C": 40, "D": 8, "E": 9, "F": 7, "G": 7, "H": 7, "I": 9, "J": 13,
             "K": 5, "L": 5, "M": 5, "N": 5, "O": 5, "P": 5, "Q": 5})
wbs.freeze_panes = "C13"

# ------------------------------------------------------------------ Q&A BANK
qa = wb.create_sheet("QA_Bank")
cell(qa, "A1", "Likely judge questions: answer outline, evidence, owner", TITLE)
header_row(qa, 3, ["#", "Question", "Answer outline", "Evidence to cite", "Owner"])
qas = [
    ("Why is this not just buying an AI camera?", "Tech at end-of-line raises scrap; value comes from where the check sits, how fast feedback travels, and who acts", "Simulation Test 1 (scenario 2 vs 4)", "M2"),
    ("What if operators don't trust the system?", "People design is in the idea: co-designed alerts, training first, overrides become kaizen input", "Exhibit 6B (31% override); dismissal chart in Simulation", "M1"),
    ("Why this pilot area?", "Largest gap between processes, clear defect-escape story, AI camera building block ready Oct 2026", "Exhibits 4, 5; gap heat map", "M2"),
    ("How confident are you in the savings?", "Base NPV + Monte Carlo probability; gate protects downside; ranges below external benchmarks", "Dashboard, Simulation Test 2/2b, Assumptions col G", "M3"),
    ("Which assumption hurts most if wrong?", "Name top tornado drivers and how the pilot tests each", "Simulation Test 3", "M3"),
    ("Why in-house instead of a vendor?", "Cheaper, flexible, connects to plant systems, builds capability; partner only for distinctive tech with knowledge transfer", "Case text on in-house strategy; Toyota insourcing (Toyota 2023)", "M2"),
    ("Will people lose jobs?", "Freed time redeployed to kaizen and new pathways; cash conversion only 50% assumed", "Assumptions row 28; Capability tab", "M1"),
    ("How does this help BEV / multi-pathway?", "Common interface + simulation-first preparation cut variant change months", "Dashboard months per variant; Exhibit 8; Siemens/Wipro PARI benchmark", "M2"),
    ("What happens if the AI camera fails validation?", "Loop is sensor-agnostic: digital andon + operator check while retraining", "Risks tab", "M2"),
    ("How do you capture senior know-how?", "Capture sprints, AI-assisted interviews validated by experts, linked to standard work", "Exhibit 6A; O-Beya precedent (Microsoft 2024)", "M1"),
    ("How is this different from what Toyota Japan does?", "Adapted to TMMIN: integrates quality loop + data standard + knowledge in one system, gated for local budget", "Ideation refs", "M1"),
    ("What do you need from TMMIN leadership now?", "Approve pilot area, Phase 0 budget, protected kaizen time, data standard ownership", "Roadmap tab", "M1"),
    ("How do you measure success?", "Outcome KPIs (cost index, scrap, months/variant) + driver KPIs (override rate, L3+ engineers, ideas)", "KPIs tab", "M3"),
    ("Why will engineers' improvement time actually rise?", "Knowledge base and citizen tools absorb routine troubleshooting", "Capability tab", "M1"),
    ("Is Rp[x]B realistic within the Rp40-120B range?", "Bottom-up by phase; pilot-light spends 25% before gate", "Assumptions rows 37, 44", "M3"),
]
for i, (q, ans, ev, own) in enumerate(qas, start=4):
    cell(qa, f"A{i}", i - 3, BOLD, border=True)
    for col, v in zip("BCDE", (q, ans, ev, own)):
        cell(qa, f"{col}{i}", v, BOLD if col == "B" else BLACK, wrap=True, border=True)
    qa.row_dimensions[i].height = 44
widths(qa, {"A": 5, "B": 40, "C": 60, "D": 42, "E": 8})

order = ["README", "WBS", "Answer_Guide", "Ideation", "Exhibits", "Assumptions", "Model", "Dashboard", "Breakeven",
         "Capability", "KPIs", "Roadmap", "Risks", "QA_Bank"]
wb._sheets = [wb[n] for n in order]
wb.save("TMMIN_Case_Model.xlsx")
print("saved")
