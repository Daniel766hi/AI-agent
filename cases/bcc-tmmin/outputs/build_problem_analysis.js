// Build outputs/Problem_Identification_Analysis.docx (Bahasa Indonesia).
// Run from the case root after outputs/build_problem_analysis.py:
//   node outputs/build_problem_analysis.js
// All numbers come from outputs/charts/problem_analysis.json (exhibits, Stage 2 diagnosis, model targets).
const fs = require("fs");
const path = require("path");
const {
  Document, Packer, Paragraph, TextRun, HeadingLevel, Table, TableRow, TableCell, WidthType, ShadingType,
  AlignmentType, ImageRun, PageOrientation, Footer, Header, PageNumber, LevelFormat, BorderStyle, PageBreak,
  VerticalAlign, TableLayoutType,
} = require("docx");

const ROOT = path.resolve(__dirname, "..");
const D = JSON.parse(fs.readFileSync(path.join(ROOT, "outputs", "charts", "problem_analysis.json"), "utf8"));
const OUT = path.join(ROOT, "outputs", "Problem_Identification_Analysis.docx");
const C = { teal: "0F3D4A", teal2: "0F7B8A", pale: "EEF3F4", amber: "F2A900", amberSoft: "FDF1CF", rust: "C2410C", ink: "13232A", muted: "53656C", line: "D5DFE1" };
const FONT = "Calibri", HEAD = "Cambria";
const W = 9638;                                  // A4 portrait content width (twips) with 2 cm margins
const WL = 14570;                                // A4 landscape content width

const idn = (x, d = 1) => {
  const s = Math.abs(x).toFixed(d).replace(".", ",").replace(/\B(?=(\d{3})+(?!\d))/g, ".");
  return (x < 0 ? "−" : "") + s;
};
const pct = (x, d = 0) => idn(x * 100, d) + "%";

// ---------------------------------------------------------------- helpers
function runs(text, base = {}) {
  // **bold** and *italic* markup inside a string
  return text.split(/(\*\*[^*]+\*\*|\*[^*]+\*)/).filter(Boolean).map((t) =>
    t.startsWith("**") ? new TextRun({ text: t.slice(2, -2), bold: true, ...base })
      : t.startsWith("*") && t.endsWith("*") && t.length > 2 ? new TextRun({ text: t.slice(1, -1), italics: true, ...base })
        : new TextRun({ text: t, ...base }));
}
const P = (text, opts = {}) => new Paragraph({ children: runs(text, opts.run || {}), spacing: { after: 120, line: 300 }, ...opts.para });
const H1 = (text) => new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun(text)] });
const H2 = (text) => new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun(text)] });
const bullet = (text, level = 0) => new Paragraph({ numbering: { reference: "bul", level }, children: runs(text), spacing: { after: 60, line: 288 } });
const numbered = (text) => new Paragraph({ numbering: { reference: "num", level: 0 }, children: runs(text), spacing: { after: 60, line: 288 } });
const caption = (text) => new Paragraph({ children: [new TextRun({ text, italics: true, size: 18, color: C.muted })], spacing: { before: 60, after: 200 } });
const source = (text) => new Paragraph({ children: [new TextRun({ text: "Sumber: " + text, size: 17, color: C.muted })], spacing: { before: 40, after: 220 } });
function callout(lines, fill = C.amberSoft) {
  return lines.map((l, i) => new Paragraph({
    children: runs(l), shading: { type: ShadingType.CLEAR, color: "auto", fill },
    spacing: { before: i === 0 ? 120 : 0, after: i === lines.length - 1 ? 200 : 60, line: 300 },
    indent: { left: 160, right: 160 },
  }));
}
function image(file, widthPx, heightPx) {
  return new Paragraph({ alignment: AlignmentType.CENTER, spacing: { before: 120, after: 40 },
    children: [new ImageRun({ type: "png", data: fs.readFileSync(path.join(ROOT, "outputs", "charts", file)), transformation: { width: widthPx, height: heightPx } })] });
}
const border = { style: BorderStyle.SINGLE, size: 4, color: C.line };
const borders = { top: border, bottom: border, left: border, right: border };
function cell(text, width, opts = {}) {
  return new TableCell({
    width: { size: width, type: WidthType.DXA }, borders, verticalAlign: VerticalAlign.CENTER,
    shading: opts.fill ? { type: ShadingType.CLEAR, color: "auto", fill: opts.fill } : undefined,
    margins: { top: 60, bottom: 60, left: 90, right: 90 },
    children: [new Paragraph({ alignment: opts.align || AlignmentType.LEFT,
      children: runs(String(text), { size: opts.size || 18, bold: opts.bold, color: opts.color }) })],
  });
}
// rows[0] is the header; widths are proportions that are scaled to the table width
function table(rows, props, total = W, opts = {}) {
  const sum = props.reduce((a, b) => a + b, 0);
  const widths = props.map((p) => Math.floor((p / sum) * total));
  widths[widths.length - 1] += total - widths.reduce((a, b) => a + b, 0);
  const num = opts.num || [];
  return new Table({
    width: { size: total, type: WidthType.DXA }, columnWidths: widths, layout: TableLayoutType.FIXED,
    rows: rows.map((r, ri) => new TableRow({ tableHeader: ri === 0, children: r.map((c, ci) => {
      if (ri === 0) return cell(c, widths[ci], { fill: C.teal, bold: true, color: "FFFFFF", size: 17 });
      const custom = opts.cellFill ? opts.cellFill(ri, ci, c) : null;
      return cell(c, widths[ci], { fill: custom || (opts.highlight && opts.highlight(ri) ? C.amberSoft : ri % 2 ? undefined : C.pale),
        align: num.includes(ci) ? AlignmentType.RIGHT : AlignmentType.LEFT, bold: opts.boldRow && opts.boldRow(ri) });
    }) })),
  });
}
const spacer = () => new Paragraph({ spacing: { after: 120 }, children: [] });

// ---------------------------------------------------------------- content
const ex = D.ex, t = D.target, k = D.calc;

const cover = [
  new Paragraph({ spacing: { before: 2600, after: 120 }, children: [new TextRun({ text: "M3C 2026 · STUDI KASUS PT TOYOTA MOTOR MANUFACTURING INDONESIA", size: 20, color: C.teal2, bold: true })] }),
  new Paragraph({ spacing: { after: 200 }, children: [new TextRun({ text: "Problem Identification & Analysis", font: HEAD, size: 60, bold: true, color: C.teal })] }),
  new Paragraph({ spacing: { after: 600 }, children: [new TextRun({ text: "Profil perusahaan, latar belakang, issue tree, dan gap analysis", size: 28, color: C.muted })] }),
  ...callout([
    "**Temuan utama.** Selisih biaya konversi TMMIN terhadap pemain baru melebar dari 6 menjadi 17 poin indeks dalam dua tahun, rata-rata 5,5 poin per tahun.",
    "Ketiga belas indikator internal yang punya data 2023 dan 2025 memburuk, dan mengembalikan kinerja ke level 2023 hanya menutup 11–19% selisih.",
    "Akar masalahnya: sinyal masalah dan pelajaran perbaikan tidak punya jalur kembali, sehingga laju belajar pabrik kalah dari pesaing. Celah terbesar ada **di antara proses**: inspeksi kualitas dan integrasi data, dua fungsi yang masih di Level 1.",
  ]),
  new Paragraph({ spacing: { before: 1800 }, children: [new TextRun({ text: "Tim [Nama Tim] · [Nama Anggota 1] · [Nama Anggota 2] · [Nama Anggota 3]", size: 20, color: C.muted })] }),
  new Paragraph({ children: [new TextRun({ text: "Exhibit 3–9 casebook adalah data dummy dari panitia. Angka turunan dihitung ulang dengan skrip di folder work/ dan model/.", size: 17, italics: true, color: C.muted })] }),
  new Paragraph({ children: [new PageBreak()] }),
];

const profile = [
  H1("1. Profil Perusahaan"),
  H2("1.1 Gambaran umum"),
  P("PT Toyota Motor Manufacturing Indonesia (TMMIN) adalah basis manufaktur Toyota di Indonesia. TMMIN mengoperasikan lima fasilitas di Jakarta Utara dan Karawang yang memproduksi kendaraan, mesin, serta komponen press dan casting."),
  P("Perusahaan sedang bergeser dari fokus *green manufacturing* menuju perusahaan mobilitas, dengan pendekatan **multi-pathway**: satu basis produksi yang menampung kendaraan konvensional (ICE), hybrid (HEV), plug-in hybrid (PHEV), dan listrik baterai (BEV) sekaligus. Periode 2026–2030 adalah jendela terbentuknya posisi kompetitif jangka panjang."),
  H2("1.2 Fasilitas produksi"),
  table(ex["2"], [1.1, 1.2, 0.6, 2.2, 2.2]),
  source("Casebook, Exhibit 2."),
  H2("1.3 Parameter operasi dan finansial Karawang"),
  P("Analisis biaya dalam dokumen ini berfokus pada perakitan kendaraan Karawang I dan II, sesuai parameter finansial yang diberikan casebook."),
  table(ex["9"], [3, 2]),
  source("Casebook, Exhibit 9."),
  H2("1.4 Tingkat otomasi per proses"),
  P("Dari dua belas proses, hanya dua yang masih di Level 1 (manual): **inspeksi kualitas** dan **integrasi data**. Keduanya bukan proses produksi, melainkan titik temu tempat sinyal antarproses seharusnya mengalir."),
  table(ex["5"], [2.2, 0.6, 4], W, { highlight: (ri) => ["1"].includes(ex["5"][ri][1]) }),
  source("Casebook, Exhibit 5 (Level 1 = manual, Level 4 = otonom). Baris berwarna: Level 1."),
  H2("1.5 Profil kompetensi engineer"),
  P("Kekuatan TMMIN ada di bidang mekanikal dan elektrikal. Kompetensi digital sangat tipis: hanya **2 dari 30** engineer Software & AI berada di Level 3 ke atas, dan tidak ada satu pun di Level 4."),
  table(ex["7"], [2, 1, 1, 1, 1], W, { num: [1, 2, 3, 4] }),
  source("Casebook, Exhibit 7 (jumlah orang per level, N = 30 per bidang)."),
];

const background = [
  new Paragraph({ children: [new PageBreak()] }),
  H1("2. Latar Belakang"),
  H2("2.1 Tekanan industri"),
  P("Industri otomotif global sedang berubah oleh empat tren teknologi: **Connected, Autonomous, Shared, dan Electric (C.A.S.E.)**. Di Indonesia, perubahan ini datang bersamaan dengan pasar domestik yang melemah dan masuknya pemain baru dengan harga agresif serta siklus peluncuran yang cepat."),
  table(ex["1"], [2, 1, 1, 1], W, { num: [1, 2, 3] }),
  source("Casebook, Exhibit 1."),
  P("Pada saat yang sama, porsi kendaraan elektrifikasi akan naik tajam. Lini yang sama harus menampung lebih banyak varian tanpa menambah biaya."),
  table(ex["8"], [2, 1, 1.4, 1.4], W, { num: [1, 2, 3], boldRow: (ri) => ri === ex["8"].length - 1 }),
  source("Casebook, Exhibit 8 (indikatif)."),
  H2("2.2 Posisi biaya TMMIN"),
  P(`Dalam dua tahun, indeks biaya konversi TMMIN naik dari 100 ke 106, sementara pemain baru turun dari 94 ke 89. TMMIN kini **sekitar 19% lebih mahal per unit**, dan selisihnya melebar rata-rata **${idn(k.widen)} poin per tahun**. Sekitar ${pct(k.share_t)} pelebaran datang dari biaya TMMIN yang naik, dan ${pct(1 - k.share_t)} dari pesaing yang terus menjadi lebih murah.`),
  image("fig_pi_gap.png", 560, 298),
  caption("Gambar 1. Selisih biaya konversi melebar setiap tahun. Sumber: Exhibit 3."),
  H2("2.3 Tiga komplikasi dari casebook"),
  table([["Komplikasi", "Inti masalah", "Bukti (2023 → 2025)"],
    ["1. Biaya dan kualitas", "Tidak bisa lagi mengandalkan volume", "Indeks biaya 106 vs pemain baru 89; scrap 100 → 108; downtime 100 → 111; cacat lolos 100 → 103"],
    ["2. Fleksibilitas lini dan sumber kapabilitas", "Lini dirancang per model; teknologi dari luar mahal dan sulit diintegrasikan", "Modifikasi varian 8 → 9 bulan; peralatan point-to-point tanpa standar antarmuka"],
    ["3. Mindset, pengetahuan, talenta", "Engineer sibuk rutinitas; know-how tidak dibagi", "65% waktu engineer untuk dukungan rutin; 48% proses kritis bergantung pada 1–2 senior; 2 dari 30 engineer mahir software & AI"]],
    [1.6, 2, 3]),
  source("Casebook; data/problem.md."),
  H2("2.4 Pertanyaan kunci dan batasan"),
  ...callout(["**Pertanyaan kunci:** Bagaimana TMMIN dapat mendefinisikan ulang cara memproduksi pada 2026–2030 dengan menggabungkan teknologi masa depan seperti AI dengan pola pikir, keterampilan, dan pengetahuan manusia, agar tetap kompetitif dalam biaya dan kualitas di era C.A.S.E.?"], C.pale),
  P("Batasan dari casebook:"),
  bullet("Jawaban harus mengubah **cara manufaktur** (proses, cara kerja, orang, pengetahuan), bukan merekomendasikan produk atau alat."),
  bullet("Solusi harus transformatif dan menempatkan manusia di pusat (tema M3C 2026: *Human-Centered AI Kaizen*)."),
  bullet("Investasi program Rp40–120 miliar; diskonto 10%; umur teknologi 5 tahun; eskalasi biaya 4% per tahun."),
];

const driverRows = D.drivers.map((r) => r.slice());
driverRows[0][0] = "Kode";
const issue = [
  new Paragraph({ children: [new PageBreak()] }),
  H1("3. Issue Tree"),
  H2("3.1 Logika pemecahan"),
  P("Issue tree memecah pertanyaan kunci menjadi driver yang bisa diukur. Level pertama disusun MECE (tidak tumpang tindih, tidak ada celah) menurut dua sumbu:"),
  bullet("**Posisi**: biaya per unit hari ini (A), kualitas hari ini (B), dan biaya menambah varian di masa depan (C)."),
  bullet("**Kecepatan**: laju perbaikan tahunan dibanding pesaing (D)."),
  P("Cabang A dipecah persis mengikuti lima komponen biaya konversi di Exhibit 9 (tenaga kerja, energi, perawatan, depresiasi, scrap), sehingga tidak ada komponen yang terlewat atau terhitung dua kali. Batas A dan B: A mengukur rupiah (termasuk biaya scrap), B mengukur cacat yang lolos ke hilir."),
];
const issueLandscape = [
  H2("3.2 Diagram issue tree"),
  image("fig_pi_issuetree.png", 860, 579),
  caption("Gambar 2. Issue tree: dari pertanyaan kunci ke driver terukur, dengan exhibit sumber setiap driver."),
];
const issue2 = [
  H2("3.3 Driver, sumber, dan tren"),
  table(driverRows, [0.85, 3.0, 0.85, 0.9, 1.1, 1.3, 1.4], W, { highlight: (ri) => driverRows[ri][1].includes("terimplementasi") }),
  source("Casebook Exhibit 1, 3, 4, 6A, 7, 8, 9; work/2_diagnosis.md."),
  H2("3.4 Tiga temuan dari issue tree"),
  numbered("**Masalahnya kecepatan, bukan hanya posisi.** Selisih biaya melebar 6 → 12 → 17 poin. Bila tren berlanjut lurus, pemain baru berada di sekitar indeks 76 pada 2030 (ilustrasi ekstrapolasi, bukan prediksi)."),
  numbered(`**Kembali ke kinerja 2023 tidak cukup.** Kenaikan scrap, waktu NVA, dan downtime hanya menjelaskan ${idn(k.drift_lo)}–${idn(k.drift_hi)} poin dari selisih 17 poin (11–19%). Sisanya struktural: eskalasi upah dan energi saja menyumbang sekitar ${idn(k.p_esc)} poin.`),
  numbered(`**Mesin perbaikan melemah.** Ide yang benar-benar diimplementasikan per engineer turun dari ${idn(k.impl23, 2)} ke ${idn(k.impl25, 2)} per tahun (${pct(k.impl25 / k.impl23 - 1)}), padahal waktu untuk perbaikan hanya turun 11% (28% → 25%). Setiap jam perbaikan juga makin sedikit hasilnya.`),
  image("fig_pi_bridge.png", 560, 262),
  caption("Gambar 3. Jembatan kenaikan indeks 100 → 106. Porsi komponen biaya konversi adalah asumsi tim (tenaga kerja 40%, energi 12%, perawatan 13%, depresiasi 25%, scrap 10%), karena casebook hanya menyebut komponennya."),
];

// heat map table, sorted by score with impact cells shaded
const heat = Object.entries(D.heat).map(([name, [lvl, c, q, f]]) => ({ name, lvl, c, q, f, gap: 4 - lvl, s: (c + q + f) * (4 - lvl), top3: D.top3[name] }))
  .sort((a, b) => b.s - a.s);
const heatRows = [["#", "Proses", "Level", "Biaya", "Kualitas", "Fleks.", "Celah (4 − level)", "Skor", "Tiga besar /27 bobot"],
  ...heat.map((h, i) => [String(i + 1), h.name, String(h.lvl), String(h.c), String(h.q), String(h.f), String(h.gap), String(h.s), `${h.top3}/27`])];
const shade = { 1: "F3F6F6", 2: "F9DCC8", 3: "EFA27C" };

const gap = [
  new Paragraph({ children: [new PageBreak()] }),
  H1("4. Gap Analysis"),
  H2("4.1 Kerangka"),
  P("Gap analysis membandingkan **kondisi saat ini** (2025, dari exhibit) dengan **titik acuan** yang bisa dipertanggungjawabkan: kinerja pesaing, kinerja TMMIN sendiri pada 2023, atau level maturitas tertinggi. Kolom target 2030 menunjukkan seberapa jauh celah realistis bisa ditutup menurut model system dynamics tim, dibanding jalur tanpa tindakan."),
  H2("4.2 Celah per dimensi"),
  table([["Dimensi", "Indikator", "Saat ini (2025)", "Titik acuan", "Target 2030 (model)", "Prioritas"],
    ["Biaya", "Indeks biaya konversi", "106 (Ex.3)", "89, pemain baru 2025, dan masih turun", `≤ ${idn(t.idx_sd, 0)} pada harga konstan 2025 (tanpa tindakan ${idn(t.idx_dn)})`, "Sangat tinggi"],
    ["Kualitas", "Indeks scrap", "108 (Ex.4)", "100, level 2023", idn(t.scrap, 0), "Tinggi"],
    ["Kualitas", "Cacat lolos ke hilir", "103 (Ex.4)", "100, level 2023", idn(t.esc, 0), "Tinggi"],
    ["Keandalan", "Unplanned downtime", "111 (Ex.4)", "100, level 2023", idn(t.down, 0), "Tinggi"],
    ["Fleksibilitas", "Bulan modifikasi per varian", "9 (Ex.4)", "8, level 2023", `${idn(t.months)} (tanpa tindakan ${idn(t.months_dn)})`, "Tinggi"],
    ["Integrasi", "Level integrasi data dan peralatan", "Level 1–2 (Ex.5)", "Level 4", "Standar data di 75% proses", "Sangat tinggi"],
    ["Orang", "Waktu engineer untuk perbaikan", "25% (Ex.6A)", "28%, level 2023", pct(t.improve), "Tinggi"],
    ["Pengetahuan", "Know-how kritis terdokumentasi", "33% (Ex.6A)", "35%, level 2023", pct(t.K), "Sedang"],
    ["Pengetahuan", "Proses bergantung 1–2 senior", "48% (Ex.6A)", "45%, level 2023", pct(t.senior), "Tinggi"],
    ["Kapabilitas digital", "Engineer Software & AI L3+", "2/30 (Ex.7)", "19/30, setara mechanical", idn(t.S), "Sangat tinggi"],
    ["Adopsi", "Operator yang mengabaikan alert", "31% (Ex.6B)", "Mendekati 0%", "10%", "Tinggi"],
    ["Perbaikan", "Ide terimplementasi per engineer", "0,67 (Ex.6A)", "1,08, level 2023", "≥ 2,4", "Sangat tinggi"]],
    [1.55, 1.9, 1.2, 1.8, 2.1, 1.05], W, { cellFill: (ri, ci, c) => (ci === 5 ? (c === "Sangat tinggi" ? "F9DCC8" : c === "Tinggi" ? C.amberSoft : undefined) : undefined) }),
  source("Casebook Exhibit 3–7; target 2030 dari model/sd_model.py (skenario Closed-Loop Kaizen v2), lihat work/7_kpis.md."),
  H2("4.3 Heat map: proses × dampak × celah maturitas"),
  P("Setiap proses dinilai dampaknya terhadap biaya, kualitas, dan fleksibilitas (1 = rendah, 3 = tinggi; penilaian tim), lalu dikalikan celah maturitasnya. Skor = (biaya + kualitas + fleksibilitas) × (4 − level). Untuk menguji ketahanan, skor dihitung ulang dengan 27 kombinasi bobot."),
  table(heatRows, [0.45, 2.4, 0.7, 0.75, 0.95, 0.8, 1.05, 0.65, 1.25], W, {
    num: [0, 2, 3, 4, 5, 6, 7, 8],
    cellFill: (ri, ci, c) => (ci >= 3 && ci <= 5 ? shade[c] : ri <= 2 ? C.amberSoft : undefined),
  }),
  source("Casebook Exhibit 5; work/2_diagnosis_calc.py. Baris berwarna: dua proses yang masuk tiga besar di 27 dari 27 kombinasi bobot."),
  P("**Bacaan:** dua fungsi teratas bukan proses produksi. Keduanya adalah titik temu tempat sinyal kualitas seharusnya berbalik ke hulu (inspeksi) dan tempat data seharusnya mengalir antarproses (integrasi data). Ini mengonfirmasi bahwa celah terbesar ada **di antara proses**."),
  H2("4.4 Celah di antara proses"),
  table(D.links, [3, 0.8, 1.8], W, { num: [1] }),
  source("work/2_diagnosis.md §4 (jumlah skor proses hulu dan titik tempat sinyalnya mendarat)."),
  H2("4.5 Akar masalah (5-whys)"),
  table(D.whys, [0.4, 2, 3.8, 1.4]),
  source("work/2_diagnosis.md §5."),
  ...callout(["**Kalimat akar masalah:** Pabrik TMMIN memecahkan masalah yang sama berulang kali karena sinyal masalah dan pelajaran perbaikan tidak punya jalur kembali, baik ke proses penyebab, ke standar bersama, maupun ke varian berikutnya. Akibatnya laju belajar pabrik kalah dari pesaing."]),
  P("Satu kalimat ini menjelaskan ketiga komplikasi casebook:"),
  table(D.complications, [1.6, 1.4, 4]),
  source("work/2_diagnosis.md §5."),
  H2("4.6 Hipotesis tandingan yang ditolak"),
  table(D.rivals, [2, 4, 1.4]),
  source("work/2_diagnosis.md §6; simulasi sealer di model/run_tests.py."),
  H2("4.7 Area prioritas"),
  P("**Area prioritas:** loop kualitas di titik deteksi, yaitu inspeksi kualitas (Level 1) dan integrasi data (Level 1), dengan sealer → inspeksi sebagai titik masuk pilot."),
  table(D.evidence, [0.4, 5, 1.4]),
  source("work/2_diagnosis.md §7."),
  P("Final assembly memiliki skor dampak tertinggi di antara proses produksi, tetapi lingkupnya lebih luas dan risikonya lebih tinggi untuk pilot pertama. Sealer dipilih karena satu-satunya proses yang oleh casebook disebut tanpa umpan balik kualitas otomatis, sinyalnya paling jelas, dan kamera AI in-house sudah ada. Final assembly menjadi gelombang rollout pertama."),
  H2("4.8 Peluang tersembunyi di data"),
  table(D.opps, [1.6, 2.6, 3]),
  source("Casebook Exhibit 5, 6B, 7, 9; work/2_diagnosis.md §8."),
  H2("4.9 Keterbatasan data"),
  bullet("Exhibit 3–9 adalah **data dummy**; kesimpulan berlaku untuk kasus, bukan klaim tentang TMMIN yang sebenarnya."),
  bullet("Porsi komponen biaya konversi tidak diberikan casebook; jembatan biaya memakai asumsi tim dan indeks diasumsikan nominal."),
  bullet("Data energi tidak tersedia sama sekali, yang sekaligus menjadi bukti celah integrasi data."),
  bullet("Survei Exhibit 6B hanya mencakup area pilot (N = 120); Exhibit 7 memakai N = 30 per bidang."),
];

// ---------------------------------------------------------------- document
const footer = () => new Footer({ children: [new Paragraph({ alignment: AlignmentType.RIGHT, children: [
  new TextRun({ text: "Problem Identification & Analysis · TMMIN · M3C 2026    ", size: 16, color: C.muted }),
  new TextRun({ children: [PageNumber.CURRENT], size: 16, color: C.muted })] })] });
const portrait = { page: { size: { width: 11906, height: 16838 }, margin: { top: 1134, bottom: 1134, left: 1134, right: 1134 } } };
const landscape = { page: { size: { width: 11906, height: 16838, orientation: PageOrientation.LANDSCAPE }, margin: { top: 1000, bottom: 1000, left: 1134, right: 1134 } } };

const doc = new Document({
  creator: "Tim [Nama Tim]", title: "Problem Identification & Analysis — TMMIN", description: "M3C 2026",
  styles: {
    default: { document: { run: { font: FONT, size: 21, color: C.ink } } },
    paragraphStyles: [
      { id: "Heading1", name: "Heading 1", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { font: HEAD, size: 34, bold: true, color: C.teal }, paragraph: { spacing: { before: 120, after: 200 }, outlineLevel: 0 } },
      { id: "Heading2", name: "Heading 2", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { font: HEAD, size: 25, bold: true, color: C.teal2 }, paragraph: { spacing: { before: 280, after: 120 }, outlineLevel: 1, keepNext: true } },
    ],
  },
  numbering: { config: [
    { reference: "bul", levels: [{ level: 0, format: LevelFormat.BULLET, text: "•", alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 400, hanging: 260 } } } }] },
    { reference: "num", levels: [{ level: 0, format: LevelFormat.DECIMAL, text: "%1.", alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 400, hanging: 300 } } } }] },
  ] },
  sections: [
    { properties: portrait, children: cover },
    { properties: portrait, footers: { default: footer() }, children: [...profile, ...background, ...issue] },
    { properties: landscape, footers: { default: footer() }, children: issueLandscape },
    { properties: portrait, footers: { default: footer() }, children: [...issue2, ...gap] },
  ],
});

Packer.toBuffer(doc).then((buf) => { fs.writeFileSync(OUT, buf); console.log("wrote", path.relative(ROOT, OUT)); });
