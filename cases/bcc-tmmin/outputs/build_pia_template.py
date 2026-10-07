"""Team paper in the official M3C 2026 Word template, with Bab 1 (Problem Identification & Analysis) written.

Run from the case root:
  python outputs/build_problem_analysis.py && python outputs/build_pia_template.py

The paper has a 7-page body for four chapters (Bab 1 Daniel, Bab 2 Danu, Bab 3-4 Rifqi), so Bab 1
is held to TWO pages: the build renders the document with LibreOffice and fails if Bab 1 runs longer.
Bab 2-4 are left as template-style placeholders for their owners.

The template keeps its cover, styles, footer and table look; only the body is replaced. Numbers
come from outputs/charts/problem_analysis.json (data/facts.md, work/2_diagnosis_calc.py,
model/sd_results.json). Facts about TMMIN that are not in the casebook cite a public source.
The table of contents is filled with page numbers read back from the render; the TOC field stays
marked dirty so Word recomputes it with its own pagination.
"""
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path
from xml.sax.saxutils import escape

import docx
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from docx.oxml import parse_xml
from docx.oxml.ns import qn
from docx.shared import Cm
from docx.text.paragraph import Paragraph
from matplotlib.patches import FancyBboxPatch

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "outputs"
TEMPLATE = OUT / "Template_Proposal_M3C2026.docx"
TARGET = OUT / "Paper_M3C2026_Bab1_Problem_Identification.docx"
TREE = OUT / "charts" / "fig_pi_issuetree_compact.png"
BAB1_MAX_PAGES = 2
W_NS = 'xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"'
NAVY, ORANGE, INK, MUTED, ALT, LINE = "1F2F6B", "E8742A", "1E2A3B", "7A8494", "F5F6F9", "D7DCE4"
FULL = 9638


def idn(x, nd=1):
    return f"{x:,.{nd}f}".replace(",", "#").replace(".", ",").replace("#", ".")


def pct(x, nd=0):
    return f"{idn(100 * x, nd)}%"


# ------------------------------------------------------------------ figure
def fig_issue_tree(D):
    """Portrait-width issue tree: question -> 4 MECE branches -> one measurable driver per line."""
    k = D["calc"]
    e4 = {r[0]: r[1:] for r in D["ex"]["4"][1:]}
    e6a = {r[0]: r[1:] for r in D["ex"]["6A"][1:]}
    e6b = {r[0]: r[1] for r in D["ex"]["6B"][1:]}
    e8 = {r[0].replace("**", ""): r[1:] for r in D["ex"]["8"][1:]}
    e3 = D["ex"]["3"]
    sw = next(r for r in D["ex"]["7"] if r[0] == "Software & AI")
    arrow = lambda key, d: f"{d[key][0]} → {d[key][1]}"
    branches = [
        (f"A. Biaya konversi per unit\n{e3[-1][1]} vs {e3[-1][2]} pemain baru", [
            f"A1 Tenaga kerja: NVA operator {arrow('Waktu non-value-added operator (% jam kerja)', e4)}%",
            f"A2 Perawatan: unplanned downtime {arrow('Unplanned downtime (indeks)', e4)}",
            f"A3 Scrap: indeks {arrow('Scrap (indeks)', e4)}",
            "A4 Energi: tidak ada data (celah data)",
            "A5 Depresiasi: utilisasi 70%, pasar −7,2%"]),
        (f"B. Kualitas: cacat ditemukan\nterlambat (lolos {arrow('Cacat lolos ke proses hilir (indeks)', e4)})", [
            "B1 Inspeksi visual manual di akhir lini (Level 1)",
            "B2 Sealer tanpa umpan balik kualitas otomatis",
            f"B3 {e6b['Sering mengabaikan alert otomatis']} operator sering mengabaikan alert"]),
        (f"C. Varian baru lambat\n{arrow('Modifikasi peralatan untuk varian baru (bulan)', e4)} bulan per varian", [
            "C1 Peralatan point-to-point, tanpa standar antarmuka",
            f"C2 Elektrifikasi {e8['Total elektrifikasi'][0]} → {e8['Total elektrifikasi'][1]}–{e8['Total elektrifikasi'][2]} (2030)",
            f"C3 Software & AI Level 3+ hanya {int(sw[3]) + int(sw[4])}/30"]),
        (f"D. Laju perbaikan kalah\nselisih +{idn(k['widen'])} poin/tahun", [
            f"D1 Waktu rutin engineer {arrow('Waktu engineer untuk dukungan rutin & troubleshooting (%)', e6a)}%",
            f"D2 Ide terimplementasi/engineer {pct(k['impl25'] / k['impl23'] - 1)}".replace("-", "−"),
            f"D3 Proses bergantung 1–2 senior {e6a['Proses kritis yang bergantung pada 1–2 senior (%)'][1]}%",
            f"D4 Hanya {e6b['Sudah dilatih alat berbasis data']} operator terlatih alat data"]),
    ]
    navy, teal, gray, line, ink = "#1F2F6B", "#DCE3F5", "#7A8494", "#C9D2EC", "#1E2A3B"
    leaves = sum(len(b[1]) for b in branches)
    gap = 0.35
    H = leaves + gap * (len(branches) - 1)
    plt.rcParams["font.family"] = ["Carlito", "DejaVu Sans"]  # Carlito is metric-compatible with the template's Calibri
    fig, ax = plt.subplots(figsize=(7.4, 4.35), dpi=250)
    ax.set_xlim(0, 10)
    ax.set_ylim(-0.5, H)
    ax.axis("off")

    def box(x, y, w, h, text, fc, ec, color=ink, size=6.6, bold=False):
        ax.add_patch(FancyBboxPatch((x, y - h / 2), w, h, boxstyle="round,pad=0.02,rounding_size=0.08", fc=fc, ec=ec, lw=0.7))
        ax.text(x + 0.08, y, text, va="center", ha="left", fontsize=size, color=color, fontweight="bold" if bold else "normal",
                linespacing=1.2)

    y, mids = H - 0.5, []
    for title, kids in branches:
        ys = []
        for name in kids:
            box(5.55, y, 4.4, 0.82, name, "#FFFFFF", line, size=8.2)
            ys.append(y)
            y -= 1
        mid = (ys[0] + ys[-1]) / 2
        mids.append(mid)
        box(2.45, mid, 2.75, 1.7, title, teal, navy, size=8.2, bold=True)
        for yy in ys:
            ax.plot([5.2, 5.38, 5.38, 5.55], [mid, mid, yy, yy], color=gray, lw=0.6)
        y -= gap
    root = (mids[0] + mids[-1]) / 2
    box(0.0, root, 2.2, 3.2, "Mengapa daya saing\nbiaya dan kualitas\nTMMIN tergerus, dan\ncelah mana yang\npaling menentukan?",
        navy, navy, color="#FFFFFF", size=8.6, bold=True)
    for m in mids:
        ax.plot([2.2, 2.32, 2.32, 2.45], [root, root, m, m], color=gray, lw=0.6)
    fig.tight_layout(pad=0.2)
    fig.savefig(TREE)
    plt.close(fig)


# ------------------------------------------------------------------ xml helpers
def runs(text, size=None, color=None, bold=False, italic=False):
    """'**bold**' and '*italic*' markup to w:r elements."""
    out = []
    for part in re.split(r"(\*\*[^*]+\*\*|\*[^*]+\*)", text):
        if not part:
            continue
        b, i = bold, italic
        if part.startswith("**"):
            part, b = part[2:-2], True
        elif part.startswith("*"):
            part, i = part[1:-1], True
        rpr = ("<w:b/><w:bCs/>" if b else "") + ("<w:i/><w:iCs/>" if i else "")
        rpr += f'<w:color w:val="{color}"/>' if color else ""
        rpr += f'<w:sz w:val="{size}"/><w:szCs w:val="{size}"/>' if size else ""
        out.append(f'<w:r><w:rPr>{rpr}</w:rPr><w:t xml:space="preserve">{escape(part)}</w:t></w:r>')
    return "".join(out)


def el(xml):
    return parse_xml(xml.replace("<w:p>", f"<w:p {W_NS}>", 1) if xml.startswith("<w:p>") else xml)


class Doc:
    def __init__(self):
        self.d = docx.Document(str(TEMPLATE))
        self.body = self.d.element.body
        kids = list(self.body.iterchildren())
        self.final_sect = kids[-1]
        self.toc_sdt = kids[13]
        for k in kids[14:-1]:  # drop the template body; keep cover, "Daftar Isi" and the TOC field
            self.body.remove(k)
        self.headings, self.fig, self.tab = [], 0, 0

    def add(self, xml):
        e = el(xml) if isinstance(xml, str) else xml
        self.final_sect.addprevious(e)
        return e

    def h1(self, text):
        self.headings.append((1, text))
        self.add(f'<w:p><w:pPr><w:pStyle w:val="Heading1"/><w:pageBreakBefore/></w:pPr>{runs(text)}</w:p>')

    def h2(self, text):
        self.headings.append((2, text))
        self.add(f'<w:p><w:pPr><w:pStyle w:val="Heading2"/><w:keepNext/><w:spacing w:before="160" w:after="60"/></w:pPr>{runs(text)}</w:p>')

    def p(self, text, after=100):
        self.add(f'<w:p><w:pPr><w:spacing w:after="{after}"/><w:jc w:val="both"/></w:pPr>{runs(text)}</w:p>')

    def key(self, text):
        self.add(f'<w:p><w:pPr><w:pBdr><w:left w:val="single" w:color="{ORANGE}" w:sz="18" w:space="8"/></w:pBdr>'
                 f'<w:spacing w:before="40" w:after="120"/><w:ind w:left="200"/><w:jc w:val="both"/></w:pPr>'
                 f'{runs(text, size=22, color=NAVY)}</w:p>')

    def placeholder(self, text):
        self.add(f'<w:p><w:pPr><w:spacing w:after="120"/></w:pPr>{runs(text, color=MUTED, italic=True)}</w:p>')

    def ref(self, text):
        self.add(f'<w:p><w:pPr><w:spacing w:after="80"/><w:ind w:left="567" w:hanging="567"/></w:pPr>{runs(text, size=20)}</w:p>')

    def figure(self, path, width_cm, title, source):
        self.fig += 1
        e = self.add('<w:p><w:pPr><w:keepNext/><w:spacing w:before="60" w:after="20" w:line="240" w:lineRule="auto"/>'
                     '<w:jc w:val="center"/></w:pPr></w:p>')
        Paragraph(e, self.d._body).add_run().add_picture(str(path), width=Cm(width_cm))
        self.add(f'<w:p><w:pPr><w:spacing w:after="100"/></w:pPr>'
                 f'{runs(f"**Gambar 1.{self.fig}** {title}. Sumber: {source}.", size=17, color=MUTED)}</w:p>')

    def table(self, rows, weights, title, source, fills=None, bold_col0=False, center=()):
        self.tab += 1
        self.add(f'<w:p><w:pPr><w:keepNext/><w:spacing w:before="80" w:after="40"/></w:pPr>'
                 f'{runs(f"**Tabel 1.{self.tab}** {title}", size=18, color=NAVY)}</w:p>')
        tot = sum(weights)
        widths = [round(FULL * w / tot) for w in weights]
        widths[-1] = FULL - sum(widths[:-1])
        border = "".join(f'<w:{s} w:val="single" w:color="{LINE}" w:sz="4"/>' for s in ("top", "left", "bottom", "right"))
        mar = ('<w:tcMar><w:top w:type="dxa" w:w="30"/><w:left w:type="dxa" w:w="90"/>'
               '<w:bottom w:type="dxa" w:w="30"/><w:right w:type="dxa" w:w="90"/></w:tcMar>')
        xml = [f'<w:tbl {W_NS}><w:tblPr><w:tblW w:type="dxa" w:w="{FULL}"/><w:tblLayout w:type="fixed"/></w:tblPr><w:tblGrid>'
               + "".join(f'<w:gridCol w:w="{w}"/>' for w in widths) + "</w:tblGrid>"]
        for ri, row in enumerate(rows):
            head = ri == 0
            tr = ['<w:tr><w:trPr><w:cantSplit/>' + ("<w:tblHeader/>" if head else "") + "</w:trPr>"]
            for ci, (cell, w) in enumerate(zip(row, widths)):
                fill = NAVY if head else ((fills(ri, ci, cell) if fills else None) or ("FFFFFF" if ri % 2 else ALT))
                jc = '<w:jc w:val="center"/>' if (ci in center and not head) else ""
                txt = runs(str(cell), size=17, color="FFFFFF" if head else INK, bold=head or (bold_col0 and ci == 0))
                tr.append(f'<w:tc><w:tcPr><w:tcW w:type="dxa" w:w="{w}"/><w:tcBorders>{border}</w:tcBorders>'
                          f'<w:shd w:val="clear" w:color="auto" w:fill="{fill}"/>{mar}</w:tcPr>'
                          f'<w:p><w:pPr><w:spacing w:after="0" w:line="240" w:lineRule="auto"/>{jc}</w:pPr>{txt}</w:p></w:tc>')
            xml.append("".join(tr) + "</w:tr>")
        self.add(parse_xml("".join(xml) + "</w:tbl>"))
        self.add(f'<w:p><w:pPr><w:spacing w:before="30" w:after="100"/></w:pPr>{runs(f"Sumber: {source}", size=16, color=MUTED)}</w:p>')

    def finish(self, pages):
        num = self.final_sect.find(qn("w:pgNumType"))
        content = self.toc_sdt.find(qn("w:sdtContent"))
        first, last = list(content)
        first_runs = first.findall(qn("w:r"))  # begin, instr, separate
        for e in list(content):
            content.remove(e)
        for n, ((lvl, text), page) in enumerate(zip(self.headings, pages)):
            body = runs(text, bold=lvl == 1, size=21 if lvl == 1 else 20) + f'<w:r><w:tab/></w:r>{runs(str(page), size=20)}'
            p = el(f'<w:p><w:pPr><w:tabs><w:tab w:val="right" w:leader="dot" w:pos="9628"/></w:tabs>'
                   f'<w:spacing w:before="{80 if lvl == 1 else 0}" w:after="40"/><w:ind w:left="{0 if lvl == 1 else 360}"/></w:pPr>{body}</w:p>')
            if n == 0:
                ppr = p.find(qn("w:pPr"))
                for r in reversed(first_runs):
                    ppr.addnext(r)
            if n == len(self.headings) - 1:
                p.append(last.find(qn("w:r")))
            content.append(p)
        assert num is not None and num.get(qn("w:start")) == "1", "template numbering should restart at the TOC"


# ------------------------------------------------------------------ content
def build(D, pages):
    ex, k = D["ex"], D["calc"]
    doc = Doc()
    gap = [int(r[1]) - int(r[2]) for r in ex["3"][1:]]
    levels = [int(r[1]) for r in ex["5"][1:]]
    e1 = {r[0]: r[1:] for r in ex["1"][1:]}
    e4 = {r[0]: r[1:] for r in ex["4"][1:]}
    e6a = {r[0]: r[1:] for r in ex["6A"][1:]}
    e6b = {r[0]: r[1] for r in ex["6B"][1:]}
    e7 = {r[0]: [int(x) for x in r[1:]] for r in ex["7"][1:]}
    e8 = {r[0].replace("**", ""): r[1:] for r in ex["8"][1:]}
    e9 = {r[0]: r[1] for r in ex["9"][1:]}
    l3 = {b: v[2] + v[3] for b, v in e7.items()}
    ctrl_lo, ctrl_hi = k["drift_lo"] / gap[-1], k["drift_hi"] / gap[-1]
    impl_drop = k["impl25"] / k["impl23"] - 1
    elec = e8["Total elektrifikasi"]
    top3 = D["top3"]

    doc.h1("Ringkasan Eksekutif")
    doc.placeholder("[Diisi setelah Bab 1–4 selesai: satu kalimat jawaban utama, masalah inti, gagasan, dan keputusan yang diminta.]")

    # ---------------- Bab 1 (maks. 2 halaman)
    doc.h1("Bab 1. Problem Identification & Analysis")
    doc.key(f"Daya saing TMMIN tergerus karena pabrik belajar lebih lambat daripada pesaingnya. Selisih biaya konversi terhadap "
            f"pemain baru melebar dari {gap[0]} menjadi {gap[-1]} poin indeks dalam dua tahun, dan celah terbesarnya berada di antara "
            f"proses, bukan di dalam satu proses.")
    doc.h2("1.1 Profil Perusahaan")
    doc.p(f"PT Toyota Motor Manufacturing Indonesia (TMMIN) dipisahkan dari PT Toyota-Astra Motor pada 2003 sebagai basis manufaktur "
          f"Toyota di Indonesia, dengan kepemilikan Toyota Motor Corporation 95% dan Astra International 5% (Toyota-Astra Motor, t.t.). "
          f"Mandatnya murni manufaktur: lima fasilitas di Sunter dan Karawang memproduksi kendaraan, mesin, serta komponen press dan "
          f"casting, dan ekspor kumulatif kendaraan utuhnya mencapai tiga juta unit pada September 2025 (CNN Indonesia, 2025). Perakitan "
          f"Karawang I dan II berkapasitas {e9['Kapasitas terpasang Karawang I & II']}, beroperasi pada utilisasi "
          f"{e9['Utilisasi 2025'].split(' ')[0]}, dengan biaya konversi {e9['Biaya konversi per unit 2025'].split(' (')[0]} per unit "
          f"atau {e9['Total biaya konversi 2025']} per tahun (AKTI & TMMIN, 2026).")
    doc.p(f"Cara TMMIN memproduksi berakar pada Toyota Production System, yang kekuatannya adalah umpan balik cepat: abnormalitas "
          f"langsung terlihat, ditangani dekat sumbernya, dan solusinya kembali menjadi standar kerja (Ohno, 1988; Spear & Bowen, 1999). "
          f"Proses produksi intinya cukup matang ({levels.count(3)} dari {len(levels)} proses di Level 3), tetapi dua fungsi penghubung, "
          f"inspeksi kualitas dan integrasi data, masih manual di Level 1. Kompetensi digital juga tipis: hanya {l3['Software & AI']} "
          f"dari 30 engineer Software & AI berada di Level 3 ke atas, dibanding {l3['Mechanical']} dari 30 di bidang mekanikal.")
    doc.h2("1.2 Latar Belakang")
    doc.p(f"Tiga tekanan bertemu pada 2026–2030. Pertama, pasar domestik menyusut: *wholesales* turun "
          f"{e1['Wholesales (unit)'][2].replace('−', '')} pada 2025 (AKTI & TMMIN, 2026). Kedua, era C.A.S.E. menaikkan keragaman produk "
          f"(McKinsey & Company, 2016). Porsi kendaraan elektrifikasi diproyeksikan naik dari {elec[0]} menjadi {elec[1]}–{elec[2]} pada "
          f"2030, didorong kebijakan percepatan kendaraan listrik (Perpres No. 55 Tahun 2019 jo. No. 79 Tahun 2023), sementara modifikasi "
          f"peralatan per varian justru memanjang dari {e4['Modifikasi peralatan untuk varian baru (bulan)'][0]} menjadi "
          f"{e4['Modifikasi peralatan untuk varian baru (bulan)'][1]} bulan. Ketiga, pemain baru terus menurunkan biaya: indeksnya turun "
          f"dari {ex['3'][1][2]} ke {ex['3'][-1][2]}, sejalan dengan pasar nyata ketika BYD meraih sekitar 36% pangsa mobil listrik pada "
          f"tahun pertamanya di Indonesia (Okezone, 2025).")
    doc.p(f"Industri juga bergeser ke manufaktur yang berpusat pada manusia (Breque et al., 2021). Ini bukan slogan bagi TMMIN: "
          f"{e6b['Sering mengabaikan alert otomatis']} operator di area pilot sering mengabaikan *alert* otomatis, dan teknologi yang tidak "
          f"dipercaya penggunanya tidak menghasilkan perbaikan.")
    doc.h2("1.3 Issue Tree")
    doc.p("Pertanyaan kunci dipecah secara MECE (Minto, 2009) menjadi posisi hari ini (A biaya, B kualitas), biaya masa depan setiap varian "
          "(C), dan laju perbaikan (D). Cabang A mengikuti lima komponen biaya konversi di Exhibit 9, sehingga tidak ada komponen yang "
          "terlewat atau terhitung ganda, dan setiap ujung cabang adalah indikator terukur (Gambar 1.1).")
    doc.p(f"Ketiga belas indikator internal yang punya data 2023 dan 2025 semuanya memburuk, dan tiga temuan menyusul. **Pertama**, "
          f"masalahnya adalah kecepatan: selisih melebar {idn(k['widen'])} poin per tahun, sekitar {pct(k['share_t'])} karena biaya TMMIN "
          f"naik dan sisanya karena pesaing makin murah. **Kedua**, kembali ke kinerja 2023 hanya menutup {pct(ctrl_lo)}–{pct(ctrl_hi)} "
          f"selisih, karena sebagian besar kenaikan biaya berasal dari eskalasi upah dan energi (berdasarkan asumsi porsi biaya tim). "
          f"**Ketiga**, ide yang diimplementasikan per engineer turun {pct(-impl_drop)}, jauh lebih dalam daripada waktu perbaikan (−11%). "
          f"Pola ini adalah *capability trap* (Repenning & Sterman, 2001): waktu tersedot untuk memadamkan masalah berulang "
          f"({e6a['Waktu engineer untuk dukungan rutin & troubleshooting (%)'][1]}% waktu engineer), sehingga kemampuan memperbaiki terus "
          f"menurun.")
    doc.figure(TREE, 15.8, "Issue tree daya saing biaya dan kualitas TMMIN (angka 2023 → 2025)", "AKTI & TMMIN (2026), Exhibit 1–9; olahan tim")
    doc.h2("1.4 Gap Analysis")
    doc.p(f"Setiap proses dinilai dampaknya terhadap biaya, kualitas, dan fleksibilitas, lalu dikalikan celah maturitasnya (4 dikurangi "
          f"level otomasi). Inspeksi kualitas dan integrasi data mendapat skor tertinggi dan masuk tiga besar di "
          f"{top3['Quality inspection']} dari 27 kombinasi bobot, disusul final assembly ({top3['Final assembly']}/27). Keduanya bukan "
          f"proses produksi, melainkan titik temu tempat sinyal antarproses seharusnya mengalir.")
    sev = {"Sangat tinggi": "F9DCC8", "Tinggi": "FCEBD9"}
    rows = [["Dimensi", "Kondisi 2025", "Titik acuan", "Prioritas"],
            ["Biaya", f"Indeks {ex['3'][-1][1]}", f"{ex['3'][-1][2]} (pemain baru, masih turun)", "Sangat tinggi"],
            ["Kualitas", f"Scrap {e4['Scrap (indeks)'][1]}; cacat lolos {e4['Cacat lolos ke proses hilir (indeks)'][1]}", "100 (level 2023)", "Tinggi"],
            ["Fleksibilitas", f"{e4['Modifikasi peralatan untuk varian baru (bulan)'][1]} bulan per varian",
             f"{e4['Modifikasi peralatan untuk varian baru (bulan)'][0]} bulan (2023)", "Tinggi"],
            ["Integrasi", "Inspeksi dan data Level 1; peralatan point-to-point", "Level 4", "Sangat tinggi"],
            ["Pengetahuan", f"{e6a['Proses kritis yang bergantung pada 1–2 senior (%)'][1]}% bergantung senior; "
                            f"{e6a['Know-how kritis terdokumentasi (% item)'][1]}% terdokumentasi",
             f"{e6a['Proses kritis yang bergantung pada 1–2 senior (%)'][0]}% dan {e6a['Know-how kritis terdokumentasi (% item)'][0]}% (2023)", "Tinggi"],
            ["Kapabilitas digital", f"Software & AI Level 3+ {l3['Software & AI']}/30", f"{l3['Mechanical']}/30 (setara mekanikal)", "Sangat tinggi"],
            ["Laju perbaikan", f"{idn(k['impl25'], 2)} ide terimplementasi per engineer", f"{idn(k['impl23'], 2)} (2023)", "Sangat tinggi"]]
    doc.table(rows, [1.3, 2.9, 2.2, 1.0], "Celah per dimensi", "AKTI & TMMIN (2026), Exhibit 3–7; olahan tim.",
              fills=lambda ri, ci, c: sev.get(c) if ci == 3 else None, bold_col0=True)
    doc.key("**Akar masalah (5-whys):** sinyal masalah dan pelajaran perbaikan tidak punya jalur kembali, ke proses penyebab, ke standar "
            "bersama, maupun ke varian berikutnya, sehingga masalah yang sama dipecahkan berulang kali.")
    doc.p(f"Kalimat ini menjelaskan ketiga komplikasi casebook: cacat ditemukan terlambat (scrap +8%), setiap varian dibangun ulang "
          f"({e4['Modifikasi peralatan untuk varian baru (bulan)'][1]} bulan), dan know-how tertahan di senior "
          f"({e6a['Proses kritis yang bergantung pada 1–2 senior (%)'][1]}%). Hipotesis tandingan tidak didukung data: "
          f"{e6b['Teknologi membantu, bukan menggantikan']} operator melihat teknologi sebagai pembantu dan "
          f"{e6b['Mau menyumbang ide bila ada kanal mudah']} mau menyumbang ide, sehingga yang kurang adalah pelatihan "
          f"({e6b['Sudah dilatih alat berbasis data']}) dan kanal, bukan kemauan. Karena itu, area prioritas adalah loop kualitas di titik "
          f"deteksi (inspeksi dan integrasi data), dengan sealer sebagai titik masuk karena satu-satunya proses yang menurut casebook belum "
          f"punya umpan balik kualitas otomatis.", after=0)

    # ---------------- Bab 2-4 placeholders for their owners
    for title, owner, subs in [
        ("Bab 2. Strategic Recommendation", "Danu", ["2.1 Visi", "2.2 Transformasi Manufaktur", "2.3 Transformasi Organisasi"]),
        ("Bab 3. Implementation Direction", "Rifqi", ["3.1 Timeline Projection", "3.2 Financial Projection", "3.3 Risk Mitigation Analysis"]),
        ("Bab 4. Expected Business Impact", "Rifqi", ["4.1 Impact Assessment"]),
    ]:
        doc.h1(title)
        doc.placeholder(f"[Kalimat kunci bab. Diisi oleh {owner}.]")
        for s in subs:
            doc.h2(s)
            doc.placeholder("[Isi subbab.]")

    doc.h1("Daftar Pustaka")
    for r in [
        "AKTI & TMMIN. (2026). *M3C 2026 casebook: Next-level kaizen: Transforming manufacturing by integrating future technology and people*. MTI-Consulting × AKTI Case Competition.",
        "Breque, M., De Nul, L., & Petridis, A. (2021). *Industry 5.0: Towards a sustainable, human-centric and resilient European industry*. Publications Office of the European Union. https://doi.org/10.2777/308407",
        "CNN Indonesia. (2025, 24 September). Perjalanan Toyota Indonesia sejak 1971 hingga gapai ekspor 3 juta unit. https://www.cnnindonesia.com/otomotif/20250924184520-579-1277368/perjalanan-toyota-indonesia-sejak-1971-hingga-gapai-ekspor-3-juta-unit",
        "McKinsey & Company. (2016). *Automotive revolution – perspective towards 2030: How the convergence of disruptive technology-driven trends could transform the auto industry*. McKinsey & Company.",
        "Minto, B. (2009). *The pyramid principle: Logic in writing and thinking* (Edisi ke-3). Pearson Education.",
        "Ohno, T. (1988). *Toyota production system: Beyond large-scale production*. Productivity Press.",
        "Okezone. (2025, 22 Januari). BYD jual 15 ribu mobil listrik pada 2024, raup 36% pangsa pasar. https://ototekno.okezone.com/read/2025/01/22/52/3106665/byd-jual-15-ribu-mobil-listrik-pada-2024-raup-36-pangsa-pasar",
        "Peraturan Presiden Republik Indonesia Nomor 55 Tahun 2019 tentang Percepatan Program Kendaraan Bermotor Listrik Berbasis Baterai (*Battery Electric Vehicle*) untuk Transportasi Jalan.",
        "Peraturan Presiden Republik Indonesia Nomor 79 Tahun 2023 tentang Perubahan atas Peraturan Presiden Nomor 55 Tahun 2019 tentang Percepatan Program Kendaraan Bermotor Listrik Berbasis Baterai (*Battery Electric Vehicle*) untuk Transportasi Jalan.",
        "Repenning, N. P., & Sterman, J. D. (2001). Nobody ever gets credit for fixing problems that never happened: Creating and sustaining process improvement. *California Management Review, 43*(4), 64–88.",
        "Spear, S., & Bowen, H. K. (1999). Decoding the DNA of the Toyota Production System. *Harvard Business Review, 77*(5), 96–106.",
        "Toyota-Astra Motor. (t.t.). *Company profile*. Diakses 7 Oktober 2026, dari https://www.toyota.astra.co.id/corporate-information/profile",
    ]:
        doc.ref(r)
    doc.placeholder("[Referensi Bab 2–4 ditambahkan oleh pemilik bab, urut abjad.]")
    doc.finish(pages)
    doc.d.save(str(TARGET))
    return doc.headings


def render(path, outdir):
    subprocess.run(["soffice", "--headless", "--convert-to", "pdf", "--outdir", str(outdir), str(path)], check=True, capture_output=True)
    return Path(outdir) / (path.stem + ".pdf")


def heading_pages(pdf, headings):
    """Printed page of each heading. Numbering restarts at 1 on the Daftar Isi page, so PDF index i is page i."""
    n = int(re.search(r"Pages:\s+(\d+)", subprocess.run(["pdfinfo", str(pdf)], capture_output=True, text=True).stdout).group(1))
    text = [subprocess.run(["pdftotext", "-f", str(i), "-l", str(i), "-layout", str(pdf), "-"], capture_output=True, text=True).stdout
            for i in range(1, n + 1)]
    norm = lambda s: re.sub(r"\s+", " ", s).strip()
    pages, start = [], 2
    while start < n and "Daftar Isi" in text[start - 1] and not any(norm(l).startswith("Ringkasan Eksekutif") and "...." not in l
                                                                   for l in text[start].splitlines()):
        start += 1
    for _, h in headings:
        key = norm(h)[:28]
        hit = next(i for i in range(start, n) if any(norm(l).startswith(key) and "...." not in l for l in text[i].splitlines()))
        pages.append(hit)
        start = hit
    return pages, n


def main():
    D = json.loads((OUT / "charts" / "problem_analysis.json").read_text())
    fig_issue_tree(D)
    with tempfile.TemporaryDirectory() as tmp:
        heads = build(D, [0] * 100)
        pages, n = heading_pages(render(TARGET, tmp), heads)
        build(D, pages)
        check, _ = heading_pages(render(TARGET, tmp), heads)
        pdf = render(TARGET, tmp)
        bab1 = heads.index((1, "Bab 1. Problem Identification & Analysis"))
        bab1_pages = check[heads.index((1, "Bab 2. Strategic Recommendation"))] - check[bab1]
        if len(sys.argv) > 1:
            subprocess.run(["cp", str(pdf), sys.argv[1]], check=True)  # optional: keep the render for review
    assert check == pages, "filling the TOC changed the pagination"
    assert bab1_pages <= BAB1_MAX_PAGES, f"Bab 1 runs {bab1_pages} pages; the budget is {BAB1_MAX_PAGES}"
    print(f"wrote {TARGET.relative_to(ROOT)}: Bab 1 = {bab1_pages} pages (budget {BAB1_MAX_PAGES}), TOC pages {dict(zip([h for _, h in heads], check))}")


if __name__ == "__main__":
    main()
