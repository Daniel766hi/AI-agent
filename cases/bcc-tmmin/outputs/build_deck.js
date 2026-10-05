// Build the presentation deck for Closed-Loop Kaizen (M3C 2026).
//
//   NODE_PATH=<folder with pptxgenjs> node outputs/build_deck.js
//
// Reads every system dynamics number from model/sd_results.json (written by
// model/sd_model.py). Financial-model numbers are constants copied from
// model/run_tests.py output; work/8_tieout.py checks them against the deck text.
// Colors are hex (portable without a theme); if THEME_SCRIPT points at the pptx
// skill's apply_theme.js, the theme palette is written too.
const path = require("path");
const fs = require("fs");
const pptxgen = require("pptxgenjs");

const ROOT = path.resolve(__dirname, "..");
const SD = JSON.parse(fs.readFileSync(path.join(ROOT, "model", "sd_results.json"), "utf8"));
const OUT = path.join(__dirname, "deck_closed_loop_kaizen.pptx");

// Financial model (model/run_tests.py, model/build_model.py) — tie-out checks these
const XL = { npv: 27.0, npvCons: -55.4, npvOpt: 102.4, runRate: 48.1, pPlan: 0.86, pLate: 0.32,
  pFront: 0.49, pNoGate: 0.73, breakEven: 19.6, idx2030: 96.9 };

const COL = { ink: "1B262C", teal: "0F3D4A", teal2: "0F7B8A", pale: "EEF3F4", amber: "F2A900",
  rust: "C2410C", gray: "7A8B92", green: "2E7D32", white: "FFFFFF", muted: "5B6770", grid: "D9E1E4" };
const THEME = { name: "Closed-Loop Kaizen", headFontFace: "Cambria", bodyFontFace: "Calibri",
  colors: { dk1: COL.ink, lt1: COL.white, dk2: COL.teal, lt2: COL.pale, accent1: COL.amber,
    accent2: COL.teal2, accent3: COL.rust, accent4: COL.gray, accent5: COL.green, accent6: COL.muted,
    hlink: COL.teal2, folHlink: COL.muted } };

// ---------------------------------------------------------------- helpers
const idn = (x, d = 1) => {
  const s = Math.abs(x).toFixed(d).replace(".", ",").replace(/\B(?=(\d{3})+(?!\d))/g, ".");
  return (x < 0 ? "−" : "") + s;
};
const idn0 = (x) => idn(x, 0);
const pct = (x) => `${Math.round(x * 100)}%`;
const S = SD.summary, E = SD.econ, MC = SD.mc;
const env = Object.fromEntries(SD.env.map((r) => [r.year, r]));
const YRS = SD.years.map(String);
const series = (pol, key, scale = 1) => SD.series[pol][key].map((v) => +(v * scale).toFixed(2));
const MCK = {
  plan: "CLK v2, pilot-light + gate", noGate: "CLK v2, pilot-light, no gate",
  frontGate: "CLK v2, front-loaded + gate", failPilot: "FAILURE (adoption 20-60%): pilot-light + gate",
  failFront: "FAILURE (adoption 20-60%): front-loaded + gate", late: "CLK v2, 1 year late + gate",
  v1: "CLK v1 (no protected time) + gate",
};

const pres = new pptxgen();
pres.layout = "LAYOUT_WIDE";                        // 13.33 x 7.5 in
pres.title = "Closed-Loop Kaizen";
pres.subject = "M3C 2026 — TMMIN case";
pres.theme = { headFontFace: THEME.headFontFace, bodyFontFace: THEME.bodyFontFace };

const W = 13.333, M = 0.6;
const FOOT = "Closed-Loop Kaizen · M3C 2026 · [Nama Tim]";

pres.defineSlideMaster({
  title: "COVER_DARK",
  background: { color: COL.teal },
  objects: [
    { placeholder: { options: { name: "title", type: "title", x: M, y: 2.2, w: 11.5, h: 1.4,
      fontFace: "Cambria", fontSize: 48, bold: true, color: COL.white, valign: "bottom", align: "left", margin: 0 }, text: "" } },
    { placeholder: { options: { name: "body", type: "body", x: M, y: 3.8, w: 11.0, h: 1.4,
      fontFace: "Calibri", fontSize: 22, color: "CFE3E8", valign: "top", align: "left", margin: 0 }, text: "" } },
  ],
});
pres.defineSlideMaster({
  title: "CONTENT",
  background: { color: COL.white },
  margin: [0.5, 0.6, 0.6, 0.6],
  objects: [
    { placeholder: { options: { name: "title", type: "title", x: M, y: 0.35, w: W - 2 * M, h: 1.15,
      fontFace: "Cambria", fontSize: 24, bold: true, color: COL.teal, valign: "top", align: "left", margin: 0 }, text: "" } },
    { text: { text: FOOT, options: { x: M, y: 7.05, w: 8, h: 0.3, fontFace: "Calibri", fontSize: 10,
      color: COL.muted, margin: 0 } } },
  ],
  slideNumber: { x: W - M - 0.6, y: 7.05, w: 0.6, h: 0.3, fontFace: "Calibri", fontSize: 10, color: COL.muted, align: "right" },
});

let objId = 0;
const nm = (s) => `${s}-${++objId}`;
function content(section, title, notes) {
  const s = pres.addSlide({ masterName: "CONTENT", sectionTitle: section });
  s.addText(title, { placeholder: "title" });
  if (notes) s.addNotes(notes);
  return s;
}
function source(s, text) {
  s.addText(`Sumber: ${text}`, { x: M, y: 6.7, w: W - 2 * M, h: 0.3, fontSize: 10, color: COL.muted,
    margin: 0, isTextBox: true, objectName: nm("source") });
}
function andon(s, n, x, y, d = 0.5) {
  s.addShape(pres.shapes.OVAL, { x, y, w: d, h: d, fill: { color: COL.amber }, line: { color: COL.amber },
    objectName: nm("andon") });
  s.addText(String(n), { x, y, w: d, h: d, align: "center", valign: "middle", fontSize: 16, bold: true,
    color: COL.ink, margin: 0, isTextBox: true, objectName: nm("andon-num") });
}
function stat(s, big, label, x, y, w, color = COL.teal2, bigSize = 40) {
  s.addText(big, { x, y, w, h: 0.85, fontFace: "Cambria", fontSize: bigSize, bold: true, color, margin: 0,
    isTextBox: true, objectName: nm("stat") });
  s.addText(label, { x, y: y + 0.85, w, h: 0.9, fontSize: 14, color: COL.ink, margin: 0, valign: "top",
    isTextBox: true, objectName: nm("stat-label") });
}
function card(s, x, y, w, h, fill = COL.pale) {
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y, w, h, rectRadius: 0.08, fill: { color: fill },
    line: { color: fill }, objectName: nm("card") });
}
function bullets(s, items, x, y, w, h, size = 16) {
  s.addText(items.map((t, i) => ({ text: t, options: { bullet: true, breakLine: i < items.length - 1 } })),
    { x, y, w, h, fontSize: size, color: COL.ink, paraSpaceAfter: 8, valign: "top", margin: 0,
      isTextBox: true, objectName: nm("bullets") });
}
const AX = { catAxisLabelColor: COL.muted, valAxisLabelColor: COL.muted, catAxisLabelFontSize: 11,
  valAxisLabelFontSize: 11, catAxisLabelFontFace: "Calibri", valAxisLabelFontFace: "Calibri",
  valGridLine: { color: COL.grid, size: 0.75 }, catGridLine: { style: "none" },
  legendFontFace: "Calibri", legendFontSize: 11, legendColor: COL.ink, titleFontFace: "Calibri",
  titleColor: COL.ink, titleFontSize: 13, dataLabelFontFace: "Calibri", dataLabelFontSize: 11,
  dataLabelColor: COL.ink };
function table(s, rows, x, y, w, colW, opts = {}) {
  const head = rows[0].map((t) => ({ text: t, options: { bold: true, color: COL.white, fill: { color: COL.teal } } }));
  const body = rows.slice(1).map((r, i) => r.map((t) => (typeof t === "object" ? t :
    { text: String(t), options: { fill: { color: i % 2 ? COL.white : COL.pale } } })));
  s.addTable([head, ...body], { x, y, w, colW, fontSize: opts.size || 13, fontFace: "Calibri", color: COL.ink,
    border: { type: "solid", pt: 0.5, color: COL.grid }, valign: "middle", margin: 0.06, autoPage: false,
    objectName: nm("table") });
}

// ---------------------------------------------------------------- 0 cover
pres.addSection({ title: "Pembuka" });
let s = pres.addSlide({ masterName: "COVER_DARK", sectionTitle: "Pembuka" });
s.addText("Closed-Loop Kaizen", { placeholder: "title" });
s.addText("Pabrik yang belajar dari dirinya sendiri, dengan orang-orang TMMIN sebagai pusatnya", { placeholder: "body" });
s.addText("[Nama Tim] · [Nama Anggota 1] · [Nama Anggota 2] · [Nama Anggota 3] · M3C 2026", { x: M, y: 6.4,
  w: 11, h: 0.4, fontSize: 14, color: "CFE3E8", margin: 0, isTextBox: true, objectName: nm("team") });
andon(s, "", M, 1.4, 0.45);

// ---------------------------------------------------------------- 1 hook
s = content("Pembuka", "Pesaing 2,5 poin lebih murah setiap tahun, TMMIN 3 poin lebih mahal: selisihnya melebar 5,5 poin per tahun",
  "Buka dengan angka ini. Exhibit 3: TMMIN 100 → 106, pemain baru 94 → 89. Separuh pelebaran datang dari pesaing yang terus membaik.");
s.addChart(pres.charts.LINE, [
  { name: "TMMIN", labels: ["2023", "2024", "2025"], values: [100, 103, 106] },
  { name: "Pemain baru", labels: ["2023", "2024", "2025"], values: [94, 91, 89] },
], { x: M, y: 1.7, w: 7.4, h: 4.8, chartColors: [COL.rust, COL.teal2], lineSize: 3, lineDataSymbolSize: 9,
  showValue: true, dataLabelPosition: "t", showLegend: true, legendPos: "b", valAxisMinVal: 85, valAxisMaxVal: 110,
  showTitle: true, title: "Indeks biaya konversi per unit, Karawang (TMMIN 2023 = 100)", ...AX, objectName: nm("chart") });
stat(s, "6 → 17", "poin selisih biaya, 2023 → 2025", 8.6, 1.9, 4.1, COL.rust);
stat(s, "19%", "TMMIN lebih mahal per unit hari ini", 8.6, 3.75, 4.1, COL.rust);
s.addText("Sekitar separuh pelebaran datang dari pesaing yang terus membaik, bukan hanya dari TMMIN yang memburuk",
  { x: 8.6, y: 5.55, w: 4.1, h: 1.0, fontSize: 14, italic: true, color: COL.muted, margin: 0, isTextBox: true, objectName: nm("note") });
source(s, "Exhibit 3 (data dummy); dekomposisi di work/2_diagnosis.md");

// ---------------------------------------------------------------- 2 executive summary
s = content("Pembuka", `Ubah cara pabrik belajar, bukan peralatannya: biaya 97–${idn0(S.clk_v2.real)} pada 2030 (vs ${idn0(S.do_nothing.real)}) dan NPV Rp${idn0(XL.npv)}–${idn0(E.clk_v2.npv)}\u00A0M`,
  "Jawaban, tiga angka, permintaan. Rentang berasal dari dua model: spreadsheet (tuas × adopsi) dan system dynamics (lebih konservatif karena kemerosotan harus dihentikan dulu).");
const cards = [
  [`97–${idn0(S.clk_v2.real)}`, `indeks biaya 2030, harga konstan 2025 (hari ini 106; tanpa tindakan ${idn(S.do_nothing.real)})`],
  [`Rp${idn0(XL.npv)}–${idn0(E.clk_v2.npv)} M`, `NPV dari Rp80 M; peluang positif ${pct(XL.pPlan).replace("%", "")}–${pct(MC[MCK.plan].p_pos)}`],
  [`2 → ${idn(S.clk_v2.S)}`, `engineer Software & AI mahir (dari 30); know-how 33% → ${pct(S.clk_v2.K)}`],
];
cards.forEach(([big, lab], i) => {
  const x = M + i * 4.1;
  card(s, x, 1.75, 3.8, 2.55);
  stat(s, big, lab, x + 0.25, 1.95, 3.35, COL.teal2, 34);
});
s.addText("Kami meminta empat keputusan kuartal ini", { x: M, y: 4.6, w: 12, h: 0.4, fontSize: 18, bold: true,
  color: COL.teal, margin: 0, isTextBox: true, objectName: nm("ask-head") });
["Rp8 M untuk pilot sealer → inspeksi, mulai Q4 2026", "Satu pemilik standar data pabrik",
  "Lindungi 30% waktu perbaikan dan kunci waktu yang dibebaskan loop", "Skalakan hanya lewat gate akhir 2027"]
  .forEach((t, i) => {
    const x = M + (i % 2) * 6.1, y = 5.15 + Math.floor(i / 2) * 0.7;
    andon(s, i + 1, x, y, 0.45);
    s.addText(t, { x: x + 0.6, y, w: 5.3, h: 0.45, fontSize: 15, color: COL.ink, valign: "middle", margin: 0,
      isTextBox: true, objectName: nm("ask") });
  });

// ---------------------------------------------------------------- 3 situation
pres.addSection({ title: "Masalah" });
s = content("Masalah", "Pasar turun 7,2% sementara elektrifikasi naik ke 55–70%: lebih banyak varian di lini yang sama, dengan biaya lebih rendah",
  "Exhibit 1 dan 8. Multi-pathway berarti lebih banyak varian di lini yang sama.");
stat(s, "−7,2%", "wholesales nasional 2025 (865.723 → 803.687 unit)", M, 1.9, 4.0, COL.rust);
stat(s, "70%", "utilisasi Karawang I & II (Ex.9): sekitar 75.000 unit kapasitas menganggur", M, 4.0, 4.0, COL.teal2);
s.addChart(pres.charts.BAR, [{ name: "Porsi elektrifikasi", labels: ["2026", "2030 moderat", "2030 agresif"], values: [30, 55, 70] }],
  { x: 5.2, y: 1.7, w: 7.5, h: 4.8, barDir: "col", chartColors: [COL.teal2], showValue: true, dataLabelPosition: "outEnd",
    dataLabelFormatCode: '0"%"', showLegend: false, valAxisMaxVal: 80, valAxisLabelFormatCode: '0"%"', showTitle: true,
    title: "Porsi volume HEV + PHEV + BEV", ...AX, objectName: nm("chart") });
source(s, "Exhibit 1, 8, 9");

// ---------------------------------------------------------------- 4 complication
s = content("Masalah", "Ke-13 indikator internal memburuk dalam dua tahun; tidak ada satu pun yang membaik",
  "Pola sistemik, bukan masalah satu departemen. Tunjukkan ide terimplementasi: 1,08 → 0,67 per engineer.");
const down = (t) => ({ text: t, options: { color: COL.rust, bold: true } });
table(s, [
  ["Indikator", "2023", "2025", "Arah"],
  ["Indeks biaya konversi", "100", "106", down("memburuk")],
  ["Scrap (indeks)", "100", "108", down("memburuk")],
  ["Unplanned downtime (indeks)", "100", "111", down("memburuk")],
  ["Cacat lolos ke hilir (indeks)", "100", "103", down("memburuk")],
  ["Waktu non-value-added operator", "20%", "22%", down("memburuk")],
  ["Bulan modifikasi per varian", "8", "9", down("memburuk")],
  ["Waktu engineer untuk perbaikan", "28%", "25%", down("memburuk")],
  ["Ide terimplementasi per engineer", "1,08", "0,67", down("−38%")],
  ["Know-how terdokumentasi", "35%", "33%", down("memburuk")],
  ["Proses bergantung 1–2 senior", "45%", "48%", down("memburuk")],
], M, 1.65, 8.2, [4.4, 1.2, 1.2, 1.4], { size: 13 });
card(s, 9.2, 1.65, 3.5, 4.75);
stat(s, "13 / 13", "indikator dengan data 2023 dan 2025 memburuk (Ex.3, 4, 6A); tabel menampilkan 10", 9.45, 1.9, 3.0, COL.rust, 40);
s.addText("Tiga lainnya: waktu rutin engineer 62% → 65%, ide diajukan 3,1 → 2,4, engineer baru mandiri 14 → 15 bulan",
  { x: 9.45, y: 4.0, w: 3.0, h: 2.2, fontSize: 14, color: COL.ink, margin: 0, valign: "top", isTextBox: true, objectName: nm("note") });
source(s, "Exhibit 3, 4, 6A; ide terimplementasi = ide per engineer × persen diimplementasikan");

// ---------------------------------------------------------------- 5 not enough
s = content("Masalah", "Kembali ke kinerja 2023 hanya menutup 11–19% selisih: masalahnya laju perbaikan, bukan kerusakan sesaat",
  "Jembatan 100 → 106 memakai porsi biaya asumsi tim. Bagian yang bisa dikendalikan hanya 1,8–3,3 dari 17 poin.");
s.addChart(pres.charts.BAR, [{ name: "Poin indeks", labels: ["Eskalasi upah & energi 4%/th", "Scrap 100 → 108", "NVA 20% → 22%",
  "Downtime 100 → 111 (maks)", "Selisih ke pemain baru 2025"], values: [4.2, 0.8, 1.0, 1.4, 17] }],
  { x: M, y: 1.7, w: 8.0, h: 4.8, barDir: "bar", chartColors: [COL.gray, COL.teal2, COL.teal2, COL.teal2, COL.rust],
    showValue: true, dataLabelPosition: "outEnd", dataLabelFormatCode: "0.0", showLegend: false, showTitle: true,
    title: "Poin indeks biaya konversi", catAxisOrientation: "maxMin", ...AX, objectName: nm("chart") });
card(s, 9.0, 1.7, 3.7, 4.8);
stat(s, "1,8–3,3", "poin dari 17 yang berasal dari kinerja yang memburuk (scrap, NVA, downtime)", 9.25, 1.95, 3.2, COL.teal2, 40);
s.addText("Memperbaiki yang rusak tidak cukup. Yang harus berubah adalah berapa poin pabrik membaik setiap tahun.",
  { x: 9.25, y: 4.3, w: 3.2, h: 2.0, fontSize: 15, bold: true, color: COL.teal, margin: 0, valign: "top", isTextBox: true, objectName: nm("note") });
source(s, "Exhibit 3, 4, 9; porsi biaya konversi adalah asumsi tim (work/2_diagnosis.md §3.2)");

// ---------------------------------------------------------------- 6 root cause
s = content("Masalah", "Pabrik memecahkan masalah yang sama berulang kali karena sinyal dan pelajaran tidak punya jalur kembali",
  "5-whys di work/2_diagnosis.md §5. Ini juga pola jebakan firefighting (Repenning & Sterman 2001).");
s.addText("Akar masalah: sinyal masalah dan pelajaran perbaikan tidak kembali ke proses penyebab, ke standar bersama, maupun ke varian berikutnya. Akibatnya laju belajar pabrik kalah dari pesaing.",
  { x: M, y: 1.6, w: W - 2 * M, h: 0.95, fontSize: 17, italic: true, color: COL.ink, margin: 0, isTextBox: true, objectName: nm("root") });
[["Ke proses penyebab", "Inspeksi Level 1 tidak mengirim hasil ke hulu; sealer tanpa umpan balik otomatis", "Scrap +8%, cacat lolos hanya +3%: cacat tertangkap, tetapi terlambat"],
  ["Ke standar bersama", "48% proses kritis bergantung pada 1–2 senior; 71% berbagi lewat coaching informal", "65% waktu engineer memadamkan masalah yang sama; ide terimplementasi −38%"],
  ["Ke varian berikutnya", "Data Level 1; peralatan point-to-point tanpa standar antarmuka", "Setiap varian baru sekitar 9 bulan pengerjaan ulang"]]
  .forEach(([h, a, b], i) => {
    const x = M + i * 4.1;
    card(s, x, 2.8, 3.8, 3.7);
    andon(s, i + 1, x + 0.25, 3.0, 0.45);
    s.addText(h, { x: x + 0.85, y: 3.0, w: 2.8, h: 0.45, fontSize: 17, bold: true, color: COL.teal, valign: "middle", margin: 0, isTextBox: true, objectName: nm("h") });
    s.addText(a, { x: x + 0.25, y: 3.65, w: 3.3, h: 1.3, fontSize: 14, color: COL.ink, margin: 0, valign: "top", isTextBox: true, objectName: nm("a") });
    s.addText(b, { x: x + 0.25, y: 5.0, w: 3.3, h: 1.3, fontSize: 14, bold: true, color: COL.rust, margin: 0, valign: "top", isTextBox: true, objectName: nm("b") });
  });
source(s, "Exhibit 4, 5, 6A, 6B");

// ---------------------------------------------------------------- 7 biggest gap
s = content("Masalah", "Celah terbesar ada di antara proses: inspeksi dan integrasi data masuk tiga besar di 27 dari 27 kombinasi bobot",
  "Skor = (biaya + kualitas + fleksibilitas) × (4 − level). Final assembly skor dampaknya tinggi; sealer dipilih untuk pilot karena sinyalnya paling jelas dan asetnya ada.");
const hl = (t) => ({ text: t, options: { bold: true, fill: { color: "FDE7A6" } } });
table(s, [
  ["Proses", "Level", "Biaya", "Kualitas", "Fleksibilitas", "Skor", "Tiga besar (27 bobot)"],
  [hl("Quality inspection"), hl("1"), hl("3"), hl("3"), hl("1"), hl("21"), hl("27/27")],
  [hl("Data integration"), hl("1"), hl("2"), hl("2"), hl("3"), hl("21"), hl("27/27")],
  ["Final assembly", "2", "3", "2", "3", "16", "21/27"],
  ["Sealer (pilot)", "2", "3", "3", "1", "14", "6/27"],
  ["Intralogistics", "2", "3", "1", "2", "12", "—"],
  ["Equipment & system integration", "2", "2", "1", "3", "12", "—"],
  ["Maintenance", "2", "3", "1", "1", "10", "—"],
], M, 1.7, 12.1, [3.7, 1.0, 1.2, 1.3, 1.6, 1.2, 2.1], { size: 14 });
s.addText("Dua teratas bukan proses produksi: keduanya titik temu tempat sinyal seharusnya berbalik ke hulu",
  { x: M, y: 5.6, w: 12, h: 0.6, fontSize: 16, bold: true, color: COL.teal, margin: 0, isTextBox: true, objectName: nm("note") });
source(s, "Exhibit 5; penilaian dampak oleh tim (work/2_diagnosis.md §4)");

// ---------------------------------------------------------------- 8 vision
pres.addSection({ title: "Gagasan" });
s = content("Gagasan", "Pada 2030, keunggulan TMMIN adalah pabrik yang belajar lebih cepat daripada yang bisa ditiru pesaing",
  "Biaya rendah adalah hasil, bukan visinya. Tiga nilai di luar biaya, semua dari model system dynamics.");
[["Kecepatan", `${idn(S.clk_v2.months)} bulan`, `per varian baru pada 2030, dibanding ${idn(S.do_nothing.months)} bila kompleksitas naik tanpa tindakan`],
  ["Pengetahuan", `33% → ${pct(S.clk_v2.K)}`, `know-how kritis terdokumentasi; proses yang bergantung pada 1–2 senior 48% → ${pct(SD.social["2030"].senior_dep)}`],
  ["Orang", `25% → ${pct(S.clk_v2.improve)}`, "waktu engineer untuk perbaikan; operator membangun alat dan menyumbang ide"]]
  .forEach(([h, big, lab], i) => {
    const x = M + i * 4.1;
    card(s, x, 1.8, 3.8, 3.6);
    andon(s, i + 1, x + 0.25, 2.05, 0.45);
    s.addText(h, { x: x + 0.85, y: 2.05, w: 2.8, h: 0.45, fontSize: 18, bold: true, color: COL.teal, valign: "middle", margin: 0, isTextBox: true, objectName: nm("h") });
    stat(s, big, lab, x + 0.25, 2.9, 3.3, COL.teal2, 36);
  });
source(s, "model/sd_model.py, skenario CLK v2; baseline Exhibit 4, 6A");

// ---------------------------------------------------------------- 9 idea
s = content("Gagasan", "Closed-Loop Kaizen: tiga loop dengan manusia di pusat, ditambah waktu perbaikan yang dilindungi",
  "Teknologi hanya membawa sinyal. Yang berubah adalah ke mana sinyal pergi, siapa yang bertindak, dan apakah ada waktu untuk memperbaiki.");
const loops = [["Loop kualitas", "Jidoka: abnormalitas kembali ke proses penyebab dalam hitungan menit"],
  ["Loop data & peralatan", "Standardized work: satu standar antarmuka; varian baru menjadi konfigurasi"],
  ["Loop manusia & pengetahuan", "Kaizen & yokoten: alat buatan sendiri, kanal ide, know-how senior tertangkap"]];
loops.forEach(([h, t], i) => {
  const x = M + i * 4.1;
  s.addShape(pres.shapes.OVAL, { x: x + 0.9, y: 1.7, w: 2.0, h: 2.0, fill: { color: COL.pale }, line: { color: COL.teal2, width: 2 }, objectName: nm("loop") });
  s.addText(h, { x: x + 0.9, y: 1.7, w: 2.0, h: 2.0, align: "center", valign: "middle", fontSize: 15, bold: true, color: COL.teal, margin: 0.1, isTextBox: true, objectName: nm("loop-t") });
  s.addText(t, { x, y: 3.85, w: 3.8, h: 1.0, fontSize: 14, color: COL.ink, margin: 0, align: "center", valign: "top", isTextBox: true, objectName: nm("loop-d") });
});
card(s, M, 5.05, 12.1, 1.4, COL.teal);
andon(s, "", M + 0.3, 5.5, 0.5);
s.addText([{ text: "Orang TMMIN di pusat: ", options: { bold: true } },
  { text: "30% waktu perbaikan dilindungi, setiap jam yang dibebaskan loop dikunci untuk perbaikan, dan pabrik dikelola dengan target laju belajar (poin indeks per tahun)" }],
  { x: M + 1.0, y: 5.15, w: 10.9, h: 1.2, fontSize: 16, color: COL.white, valign: "middle", margin: 0, isTextBox: true, objectName: nm("band") });
source(s, "work/3_options.md, work/4_scoring.md");

// ---------------------------------------------------------------- 10 how it works
s = content("Gagasan", "Satu siklus di sealer: deteksi, rutekan, bertindak, belajar, standarkan. Hari ini langkah 2, 4, dan 5 tidak ada",
  "Langkah 2, 4, dan 5 yang hilang. Itulah sebabnya kamera saja tidak menyelesaikan masalah.");
[["Deteksi", "Kamera, sensor, atau operator menemukan bead sealer yang terlewat", true],
  ["Rutekan", "Standar data mengirim sinyal ke stasiun sealer dalam hitungan detik", false],
  ["Bertindak", "Operator stop, koreksi, konfirmasi: jidoka di stasiun", true],
  ["Belajar", "Team leader meninjau penyebab dan setiap alert yang diabaikan di kaizen harian", false],
  ["Standarkan", "Perbaikan masuk standard work dan disebar ke lini lain (yokoten)", false]]
  .forEach(([h, t, exists], i) => {
    const x = M + i * 2.45;
    card(s, x, 1.9, 2.25, 4.0, exists ? COL.pale : "FFF4D6");
    andon(s, i + 1, x + 0.2, 2.1, 0.5);
    s.addText(h, { x: x + 0.2, y: 2.75, w: 1.9, h: 0.5, fontSize: 18, bold: true, color: COL.teal, margin: 0, isTextBox: true, objectName: nm("h") });
    s.addText(t, { x: x + 0.2, y: 3.3, w: 1.9, h: 1.9, fontSize: 14, color: COL.ink, margin: 0, valign: "top", isTextBox: true, objectName: nm("t") });
    s.addText(exists ? (i === 0 ? "Sebagian ada" : "Ada, tetapi terlambat") : "Hilang hari ini",
      { x: x + 0.2, y: 5.3, w: 1.9, h: 0.4, fontSize: 13, bold: true, color: exists ? COL.muted : COL.rust, margin: 0, isTextBox: true, objectName: nm("state") });
  });
source(s, "data/ideation.md; Exhibit 5 (sealer: belum ada umpan balik kualitas otomatis)");

// ---------------------------------------------------------------- 11 proof 1
pres.addSection({ title: "Bukti" });
s = content("Bukti", "Kamera yang lebih baik saja menaikkan scrap 12%; menutup loop memangkasnya 85%",
  "Simulasi drift sealer, 175.000 unit, 300 simulasi. Kamera menemukan lebih banyak cacat tetapi terlambat. Kepercayaan operator bernilai: 31% alert diabaikan berarti manfaat 64%.");
s.addChart(pres.charts.BAR, [{ name: "Indeks scrap area pilot", labels: ["Hari ini: visual di akhir", "Kamera lebih baik di akhir", "Loop, 31% alert diabaikan", "Loop berpusat manusia"],
  values: [100, 111.7, 33.3, 15.3] }],
  { x: M, y: 1.7, w: 8.3, h: 4.8, barDir: "col", chartColors: [COL.gray, COL.rust, COL.teal2, COL.teal2], showValue: true,
    dataLabelPosition: "outEnd", dataLabelFormatCode: "0", showLegend: false, valAxisMinVal: 0, valAxisMaxVal: 125, showTitle: true,
    title: "Indeks scrap area pilot (hari ini = 100)", ...AX, objectName: nm("chart") });
stat(s, "+12%", "scrap dengan kamera lebih baik saja: cacat tetap ditemukan terlambat", 9.3, 1.9, 3.4, COL.rust);
stat(s, "−85%", "scrap dengan loop tertutup dan alert yang dipercaya operator", 9.3, 4.0, 3.4, COL.teal2);
source(s, "Simulasi Monte Carlo drift sealer tim (model/run_tests.py); parameter proses ilustratif");

// ---------------------------------------------------------------- 12 proof 2
s = content("Bukti", "Hanya Closed-Loop Kaizen yang membalik tren biaya; teknologi saja lebih buruk daripada tanpa tindakan",
  "Model stock-and-flow, dikalibrasi ke Ex.4/6A 2023–2025 (galat < 3%). Program SDM saja membangun orang, tetapi sinyal tetap terlambat.");
s.addChart(pres.charts.LINE, [
  { name: "Tanpa tindakan", labels: YRS, values: series("do_nothing", "cost_idx_real") },
  { name: "Beli teknologi saja", labels: YRS, values: series("tech_only", "cost_idx_real") },
  { name: "Program SDM saja", labels: YRS, values: series("people_only", "cost_idx_real") },
  { name: "Closed-Loop Kaizen", labels: YRS, values: series("clk_v2", "cost_idx_real") },
], { x: M, y: 1.7, w: 8.6, h: 4.8, chartColors: [COL.gray, COL.rust, COL.green, COL.teal2], lineSize: 2,
  lineDataSymbol: "none", showLegend: true, legendPos: "b", valAxisMinVal: 95, valAxisMaxVal: 125,
  valAxisLabelFormatCode: "0", showTitle: true, title: "Indeks biaya konversi, harga konstan 2025", ...AX, objectName: nm("chart") });
stat(s, idn(S.clk_v2.real), `indeks biaya 2030 dengan Closed-Loop Kaizen (spreadsheet: ${idn(XL.idx2030)})`, 9.6, 1.9, 3.1, COL.teal2);
stat(s, idn(S.do_nothing.real), `tanpa tindakan; beli teknologi saja ${idn(S.tech_only.real)}`, 9.6, 4.0, 3.1, COL.rust);
source(s, "model/sd_model.py; kalibrasi dan keterbatasan di work/5_tests.md");

// ---------------------------------------------------------------- 13 people
s = content("Bukti", `Waktu perbaikan naik dari 25% ke ${pct(S.clk_v2.improve)}, dan ketergantungan pada 1–2 senior turun dari 48% ke ${pct(SD.social["2030"].senior_dep)}`,
  "Melindungi 35–40% sejak awal terbukti merugikan; kami melindungi norma 30% dan mengunci waktu yang dibebaskan loop. Tanpa perlindungan, gate salah berhenti di 46% simulasi.");
s.addChart(pres.charts.LINE, [
  { name: "Tanpa tindakan", labels: YRS, values: series("do_nothing", "I", 100) },
  { name: "Program SDM saja", labels: YRS, values: series("people_only", "I", 100) },
  { name: "Closed-Loop Kaizen", labels: YRS, values: series("clk_v2", "I", 100) },
], { x: M, y: 1.7, w: 7.6, h: 4.8, chartColors: [COL.gray, COL.green, COL.teal2], lineSize: 2, lineDataSymbol: "none",
  showLegend: true, legendPos: "b", valAxisMinVal: 10, valAxisMaxVal: 50, valAxisLabelFormatCode: '0"%"', showTitle: true,
  title: "Porsi waktu engineer untuk perbaikan", ...AX, objectName: nm("chart") });
stat(s, `0,67 → ${idn(S.clk_v2.ideas)}`, "ide terimplementasi per engineer per tahun (2030)", 8.6, 1.9, 4.1, COL.teal2, 36);
stat(s, `${pct(MC[MCK.v1].gate_stop)} vs ${pct(MC[MCK.plan].gate_stop)}`, "simulasi di mana gate salah berhenti, tanpa vs dengan waktu yang dilindungi", 8.6, 4.0, 4.1, COL.teal2, 36);
source(s, "model/sd_model.py; Exhibit 6A");

// ---------------------------------------------------------------- 14 alternatives
s = content("Bukti", "Tidak ada opsi tunggal yang cukup; gabungannya menjadi #1 di sekitar 90% dari 20.000 kombinasi bobot",
  "12 opsi, 7 kriteria termasuk laju belajar. Tanpa opsi gabungan, empat opsi tunggal bergantian menang.");
table(s, [
  ["Opsi yang ditolak", "Mengapa gagal bila berdiri sendiri"],
  ["Kamera AI di seluruh lini", `Scrap +12% (simulasi); NPV ${idn(E.tech_only.npv)} M, peluang positif ${pct(MC["Buy technology only"].p_pos)} (system dynamics)`],
  ["Lini tanpa konveyor + AGV/AMR", "Padat modal; rekomendasi alat; sulit masuk Rp40–120 M"],
  ["Predictive maintenance saja", "Tidak menyentuh loop kualitas dan pengetahuan"],
  ["Program SDM saja", `Sinyal tetap terlambat; indeks biaya 2030 masih ${idn(S.people_only.real)}`],
  ["Pelatihan saja", "Keterampilan tanpa jalur balik tidak mengubah hasil; baru 18% operator terlatih"],
], M, 1.7, 8.3, [3.0, 5.3], { size: 14 });
card(s, 9.2, 1.7, 3.5, 3.4);
stat(s, "≈90%", "kombinasi bobot acak di mana Closed-Loop Kaizen peringkat pertama; tetap #1 bila kelayakannya diberi skor terburuk", 9.45, 1.95, 3.0, COL.teal2, 44);
source(s, "work/4_scoring.py (20.000 bobot Dirichlet); model/sd_model.py");

// ---------------------------------------------------------------- 15 roadmap
pres.addSection({ title: "Rencana" });
s = content("Rencana", "Hanya 25% investasi dikeluarkan sebelum gate akhir 2027; sisanya hanya berdasarkan bukti",
  "Gate: scrap pilot −60%, pengabaian alert ≤ 20%, adopsi ≥ 80%, loop di semua shift, ide ≥ 0,75 per engineer, waktu perbaikan ≥ 30%. Controller menilai secara independen.");
const phases = [["Persiapan", "Q4 2026", "10%", "Loop sealer di CCTV; kanal ide; akademi kohort 1"],
  ["Pilot", "2027", "15%", "Loop semua shift; 3 alat buatan sendiri; 20 know-how"],
  ["Standardisasi", "2028", "40%", "Final assembly & painting; standar data wajib"],
  ["Roll-out", "2029", "25%", "Semua lini kendaraan Karawang I & II"],
  ["Skala", "2030", "10%", "Pabrik mesin; varian lewat konfigurasi"]];
phases.forEach(([h, when, share, t], i) => {
  const x = M + i * 2.45 + (i >= 2 ? 0.0 : 0);
  card(s, x, 1.9, 2.25, 3.4, i < 2 ? "FFF4D6" : COL.pale);
  s.addText(h, { x: x + 0.15, y: 2.0, w: 1.95, h: 0.45, fontSize: 17, bold: true, color: COL.teal, margin: 0, isTextBox: true, objectName: nm("h") });
  s.addText(`${when} · ${share}`, { x: x + 0.15, y: 2.45, w: 1.95, h: 0.4, fontSize: 14, bold: true, color: COL.teal2, margin: 0, isTextBox: true, objectName: nm("w") });
  s.addText(t, { x: x + 0.15, y: 2.95, w: 1.95, h: 2.2, fontSize: 14, color: COL.ink, margin: 0, valign: "top", isTextBox: true, objectName: nm("t") });
});
s.addShape(pres.shapes.DIAMOND, { x: M + 2 * 2.45 - 0.42, y: 5.45, w: 0.65, h: 0.65, fill: { color: COL.amber }, line: { color: COL.amber }, objectName: nm("gate") });
s.addText("Gate akhir 2027: enam kriteria terukur; bila gagal, 75% belanja ditahan", { x: M + 2 * 2.45 + 0.35, y: 5.45, w: 7.0, h: 0.65,
  fontSize: 15, bold: true, color: COL.ink, valign: "middle", margin: 0, isTextBox: true, objectName: nm("gate-t") });
s.addText("Pelihara 2031+: audit standar, penggantian teknologi sekitar Rp16 M per tahun", { x: M, y: 6.2, w: 12, h: 0.4,
  fontSize: 14, italic: true, color: COL.muted, margin: 0, isTextBox: true, objectName: nm("sustain") });
source(s, "work/6_roadmap.md; porsi investasi sama di kedua model");

// ---------------------------------------------------------------- 16 first 100 days
s = content("Rencana", "Seratus hari pertama hanya memakai aset yang sudah ada: kamera CCTV tervalidasi, operator, dan team leader",
  "Kecepatan adalah risiko terbesar: terlambat satu tahun berarti peluang NPV positif 21–32%.");
[["Hari 1–30", "Lihat", ["Genchi genbutsu di sealer → inspeksi", "Baseline scrap dan alert yang diabaikan", "Tunjuk pemilik standar data; luncurkan kanal ide"]],
  ["Hari 31–60", "Hubungkan", ["Kamera tervalidasi ke alert sealer dan andon", "Aturan alert dirancang bersama team leader", "Sprint pertama know-how senior"]],
  ["Hari 61–100", "Jalankan", ["Loop di satu shift, lalu semua shift", "Kaizen mingguan untuk setiap alert yang diabaikan", "Kohort akademi membangun alat pertama"]]]
  .forEach(([when, h, items], i) => {
    const x = M + i * 4.1;
    card(s, x, 1.8, 3.8, 4.6);
    andon(s, i + 1, x + 0.25, 2.0, 0.5);
    s.addText([{ text: h, options: { bold: true, color: COL.teal, fontSize: 20, breakLine: true } }, { text: when, options: { color: COL.muted, fontSize: 14 } }],
      { x: x + 0.9, y: 1.95, w: 2.7, h: 0.8, margin: 0, valign: "top", isTextBox: true, objectName: nm("h") });
    bullets(s, items, x + 0.3, 3.05, 3.25, 3.2, 15);
  });
source(s, "work/6_roadmap.md §4");

// ---------------------------------------------------------------- 17 capability
s = content("Rencana", `Engineer Software & AI mahir naik dari 2 ke ${idn(S.clk_v2.S)}, dan TMMIN membangun sendiri apa yang menjadi pembeda`,
  "Laju akademi: L1→L2 30%/tahun, L2→L3 20%/tahun. Laju ini juga membatasi rollout di model. Mitra hanya untuk pilot dan teknologi khusus, dengan transfer pengetahuan.");
s.addChart(pres.charts.LINE, [{ name: "Engineer SW & AI L3+", labels: YRS.slice(2, 8), values: series("clk_v2", "S").slice(2, 8) }],
  { x: M, y: 1.7, w: 6.0, h: 4.8, chartColors: [COL.teal2], lineSize: 3, lineDataSymbolSize: 8, showValue: true,
    dataLabelPosition: "t", dataLabelFormatCode: "0.0", showLegend: false, valAxisMinVal: 0, valAxisMaxVal: 16,
    showTitle: true, title: "Engineer Software & AI di L3+ (dari 30), rata-rata tahunan", ...AX, objectName: nm("chart") });
table(s, [
  ["Komponen", "Pilihan"],
  ["Logika loop dan aturan alert", "Bangun"],
  ["Standar antarmuka dan data", "Bangun"],
  ["Model inspeksi AI", "Bangun"],
  ["Peralatan dan fixture standar", "Bangun"],
  ["Komputasi dan cloud", "Mitra"],
  ["Loop pertama di pilot", "Mitra, sementara"],
  ["Sensor canggih, proses baterai", "Mitra"],
], 7.0, 1.7, 5.7, [3.7, 2.0], { size: 14 });
s.addText("Setiap kontrak mitra: engineer berpasangan, dokumentasi dalam standar TMMIN, serah terima sebagai syarat pembayaran akhir",
  { x: 7.0, y: 5.6, w: 5.7, h: 0.9, fontSize: 13, italic: true, color: COL.muted, margin: 0, isTextBox: true, objectName: nm("note") });
source(s, "Exhibit 7; model/sd_model.py; work/6_roadmap.md §5–6");

// ---------------------------------------------------------------- 18 financials
pres.addSection({ title: "Dampak" });
s = content("Dampak", `Program Rp80 M menghasilkan NPV Rp${idn0(XL.npv)}–${idn0(E.clk_v2.npv)} M dan sudah impas bila menutup 22% selisih biaya`,
  `Spreadsheet: run-rate Rp${idn(XL.runRate)} M/tahun (8,6% biaya konversi). System dynamics: NPV Rp${idn(E.clk_v2.npv)} M vs tanpa tindakan; terhadap kinerja yang dibekukan di 2025, NPV 2026–30 ${idn(E.clk_v2.npv_frozen)} M dan 2026–35 Rp${idn(E.clk_v2.npv35_frozen)} M.`);
s.addChart(pres.charts.BAR, [{ name: "NPV 2026–2030", labels: ["Konservatif (Rp110 M)", "Dasar (Rp80 M)", "Optimis (Rp60 M)"], values: [XL.npvCons, XL.npv, XL.npvOpt] }],
  { x: M, y: 1.7, w: 7.2, h: 4.8, barDir: "col", chartColors: [COL.rust, COL.teal2, COL.teal2], showValue: true,
    dataLabelPosition: "outEnd", dataLabelFormatCode: "0.0", showLegend: false, showTitle: true,
    title: "NPV per skenario, model finansial (Rp miliar, 10%)", ...AX, objectName: nm("chart") });
stat(s, `Rp${idn(E.clk_v2.npv)} M`, "NPV di model system dynamics, vs tanpa tindakan; payback 2030", 8.2, 1.85, 4.5, COL.teal2, 36);
stat(s, "22%", `selisih biaya yang perlu tertutup agar impas (penghematan tahun pertama Rp${idn(XL.breakEven)} M)`, 8.2, 3.65, 4.5, COL.teal2, 36);
s.addText(`Batas bawah yang jujur: bila kinerja 2025 bisa dibekukan tanpa usaha, NPV 2026–30 ${idn(E.clk_v2.npv_frozen)} M; 2026–35 Rp${idn(E.clk_v2.npv35_frozen)} M`,
  { x: 8.2, y: 5.45, w: 4.5, h: 1.1, fontSize: 13, italic: true, color: COL.muted, margin: 0, valign: "top", isTextBox: true, objectName: nm("note") });
source(s, "model/build_model.py (Exhibit 9: 175.000 unit × Rp3,2 juta, diskonto 10%, eskalasi 4%); model/sd_model.py");

// ---------------------------------------------------------------- 19 stress
s = content("Dampak", "Kecepatan menentukan: terlambat setahun, peluang NPV positif turun ke 21–32%; pilot-light adalah asuransi",
  "Belanja di awal lebih untung bila loop berhasil, tetapi bila gagal peluang NPV positif hanya 60% vs 90% dengan pilot-light. Kami membayar premi itu dengan sadar; gate mengizinkan percepatan.");
const stressRows = [["Rencana: pilot-light + gate", MCK.plan], ["Pilot-light tanpa gate", MCK.noGate], ["Belanja di awal + gate", MCK.frontGate],
  ["Loop gagal: pilot-light + gate", MCK.failPilot], ["Loop gagal: belanja di awal + gate", MCK.failFront], ["Rencana, terlambat 1 tahun", MCK.late]];
s.addChart(pres.charts.BAR, [{ name: "P(NPV>0)", labels: stressRows.map((r) => r[0]), values: stressRows.map((r) => Math.round(MC[r[1]].p_pos * 100)) }],
  { x: M, y: 1.7, w: 7.8, h: 4.8, barDir: "bar", chartColors: [COL.teal2, COL.gray, COL.gray, COL.teal2, COL.rust, COL.rust],
    showValue: true, dataLabelPosition: "outEnd", dataLabelFormatCode: '0"%"', showLegend: false, valAxisMinVal: 0, valAxisMaxVal: 110,
    valAxisLabelFormatCode: '0"%"', catAxisOrientation: "maxMin", showTitle: true,
    title: "Peluang NPV > 0, model system dynamics (1.500 simulasi)", ...AX, objectName: nm("chart") });
table(s, [
  ["Model finansial (10.000 simulasi)", "P(NPV>0)"],
  ["Pilot-light + gate (rencana)", pct(XL.pPlan)],
  ["Pilot-light tanpa gate", pct(XL.pNoGate)],
  ["Belanja di awal tanpa gate", pct(XL.pFront)],
  ["Rencana, terlambat 1 tahun", pct(XL.pLate)],
], 8.7, 1.7, 4.0, [2.65, 1.35], { size: 13 });
s.addText("Kedua model sepakat soal kecepatan. Mereka berbeda soal belanja di awal karena hanya system dynamics yang mengaitkan cakupan loop dengan belanja",
  { x: 8.7, y: 4.4, w: 4.0, h: 2.0, fontSize: 14, color: COL.ink, margin: 0, valign: "top", isTextBox: true, objectName: nm("note") });
source(s, "model/run_tests.py; model/sd_model.py (18 input segitiga, termasuk uji kegagalan adopsi 20–60%)");

// ---------------------------------------------------------------- 20 sustainability
s = content("Dampak", `Sekitar ${idn0(env[2030].tco2)} t CO₂ per tahun dihindari dan scrap −40%; hasilnya bertahan selama cara kerja dipertahankan`,
  "Listrik PLN I-3 Rp1.114,74/kWh; grid Jamali 0,80 tCO2/MWh; 70% biaya energi listrik (asumsi). Dampak CO2 kecil; manfaat lingkungan terbesar adalah material yang tidak terbuang.");
s.addChart(pres.charts.BAR, [{ name: "t CO2 dihindari", labels: SD.env.map((r) => String(r.year)), values: SD.env.map((r) => Math.round(r.tco2)) }],
  { x: M, y: 1.7, w: 6.2, h: 4.8, barDir: "col", chartColors: [COL.green], showValue: false, showLegend: false,
    showTitle: true, title: "CO₂ dihindari dari loop energi (ton per tahun)", ...AX, objectName: nm("chart") });
s.addChart(pres.charts.LINE, [
  { name: "Cara kerja dipertahankan", labels: YRS, values: series("clk_v2", "cost_idx_real") },
  { name: "Program dihentikan 2031", labels: YRS, values: series("clk_v2_relapse", "cost_idx_real") },
  { name: "Tanpa tindakan", labels: YRS, values: series("do_nothing", "cost_idx_real") },
], { x: 7.0, y: 1.7, w: 5.7, h: 3.3, chartColors: [COL.teal2, COL.rust, COL.gray], lineSize: 2, lineDataSymbol: "none",
  catAxisLabelFrequency: 2,
  showLegend: true, legendPos: "b", valAxisMinVal: 95, valAxisMaxVal: 125, showTitle: true,
  title: "Indeks biaya, harga konstan 2025", ...AX, objectName: nm("chart") });
s.addText([{ text: `Ketahanan 2035: ${idn(S.clk_v2.real2035)} vs ${idn(S.clk_v2_relapse.real2035)} bila dihentikan. `, options: { bold: true } },
  { text: `Sosial 2030: ketergantungan pada senior 48% → ${pct(SD.social["2030"].senior_dep)}; tanpa PHK (50% waktu yang dibebaskan dialihkan ke kaizen).` }],
  { x: 7.0, y: 5.15, w: 5.7, h: 1.4, fontSize: 14, color: COL.ink, margin: 0, valign: "top", isTextBox: true, objectName: nm("note") });
source(s, "model/sd_model.py; Kepmen ESDM 163.K/2021; tarif PLN 2025");

// ---------------------------------------------------------------- 21 KPIs
s = content("Dampak", "Target pilot sekaligus kriteria gate: scrap pilot −60%, alert diabaikan ≤ 20%, ide ≥ 0,75 per engineer",
  "Delapan target draf lama diturunkan agar konsisten dengan model (lampiran A3).");
table(s, [
  ["KPI", "Baseline", "Gate 2027", "Target 2030"],
  ["Indeks biaya konversi (harga konstan 2025)", "106", "—", `≤ ${idn0(S.clk_v2.real)} (potensi ${idn(XL.idx2030)})`],
  ["Laju belajar: perubahan indeks per tahun", "+3", "Berhenti naik", "≤ −3"],
  ["Penurunan scrap area pilot", "0%", "≥ 60%", "—"],
  ["Indeks scrap pabrik", "108", "—", idn0(S.clk_v2.scrap)],
  ["Operator yang mengabaikan alert", "31%", "≤ 20%", "10%"],
  ["Waktu engineer untuk perbaikan", "25%", "≥ 30%", pct(S.clk_v2.improve)],
  ["Ide terimplementasi per engineer", "0,67", "≥ 0,75", "≥ 2,4"],
  ["Know-how kritis terdokumentasi", "33%", "39%", pct(S.clk_v2.K)],
  ["Engineer Software & AI L3+", "2", "4,9", idn(S.clk_v2.S)],
  ["CO₂ dihindari (t/tahun)", "0", "—", idn0(env[2030].tco2)],
], M, 1.65, 12.1, [5.3, 1.9, 2.3, 2.6], { size: 13 });
source(s, "work/7_kpis.md; Exhibit 3, 4, 6A, 6B, 7; model/sd_model.py");

// ---------------------------------------------------------------- 22 ask
pres.addSection({ title: "Penutup" });
s = pres.addSlide({ masterName: "COVER_DARK", sectionTitle: "Penutup" });
s.addText("Empat keputusan kuartal ini", { placeholder: "title" });
s.addText("Pabrik yang kembali belajar dimulai dari satu loop di sealer", { placeholder: "body" });
["Setujui Rp8 M untuk pilot sealer → inspeksi, mulai Q4 2026", "Tunjuk satu pemilik standar data pabrik",
  "Lindungi 30% waktu perbaikan; kunci setiap jam yang dibebaskan loop", "Skalakan hanya lewat gate akhir 2027, dan anggarkan pemeliharaan setelah 2030"]
  .forEach((t, i) => {
    const y = 4.75 + i * 0.55;
    andon(s, i + 1, M, y, 0.42);
    s.addText(t, { x: M + 0.6, y, w: 11, h: 0.42, fontSize: 17, color: COL.white, valign: "middle", margin: 0, isTextBox: true, objectName: nm("ask") });
  });
s.addNotes("Tutup dengan permintaan. Rujuk ke slide 15 untuk kriteria gate.");

// ---------------------------------------------------------------- appendix
pres.addSection({ title: "Lampiran" });
s = content("Lampiran", "A1. Model system dynamics mereproduksi 2023–2025 sebelum dipakai untuk membandingkan kebijakan",
  "Stok: kolam masalah, kapabilitas perbaikan, know-how, engineer per level, kepatuhan alert, cakupan loop dan standar data. Penahan: lantai masalah 85%, produktivitas maks 2×, firefighting membersihkan gejala.");
table(s, [
  ["Variabel (tanpa tindakan, 2025)", "Model", "Exhibit"],
  ["Indeks scrap", "1,080", "1,08 (Ex.4)"],
  ["Ide terimplementasi per engineer", "0,670", "0,67 (Ex.6A)"],
  ["Know-how terdokumentasi", "33,0%", "33% (Ex.6A)"],
  ["Waktu rutin engineer", "65,2%", "65% (Ex.6A)"],
  ["Bulan modifikasi per varian", "9,0", "9 (Ex.4)"],
  ["Waktu NVA operator", "22,0%", "22% (Ex.4)"],
  ["Indeks biaya 2024 / 2025", "103,1 / 106,6", "103 / 106 (Ex.3)"],
], M, 1.7, 7.2, [3.6, 1.6, 2.0], { size: 14 });
bullets(s, ["Loop R1: jebakan firefighting (Repenning & Sterman 2001)", "Loop R2: belajar (perbaikan → know-how → waktu bebas)",
  "Loop R3: kapabilitas (akademi → engineer L3+ → rollout)", "Loop B1: kepercayaan operator terhadap alert",
  "Skrip menolak berjalan bila kalibrasi meleset > 3%"], 8.1, 1.7, 4.6, 4.6, 14);
source(s, "model/sd_model.py; work/5_tests.md §1.2, §10");

s = content("Lampiran", "A2. Setiap tuas berada di bawah benchmark eksternal",
  "Asumsi spreadsheet dan hasil system dynamics sama-sama di bawah benchmark publik.");
table(s, [
  ["Tuas", "Benchmark eksternal", "Spreadsheet", "System dynamics 2030 vs 2025"],
  ["Scrap", "Simulasi tim: −85% di area loop × 40% cakupan", "−35%", "−27%"],
  ["Downtime / perawatan", "McKinsey: biaya −18–25%, downtime hingga −50%", "biaya −10%", "downtime −19%"],
  ["Waktu NVA operator", "Toyota AI Platform >10.000 jam/tahun", "−30%", "−24%"],
  ["Energi", "Nissan AS +13,8% dalam 3 tahun", "−5%", "−5% (cakupan penuh)"],
  ["Modifikasi varian", "Virtual commissioning −70% (Wipro PARI), −40% (Kalypso)", "biaya −35%", "bulan −20%"],
], M, 1.7, 12.1, [2.6, 5.1, 1.8, 2.6], { size: 14 });
source(s, "data/research.md; work/5_tests.md §6");

s = content("Lampiran", "A3. Koreksi terbuka: target yang kami turunkan setelah model system dynamics",
  "Bila pengukuran bertentangan dengan harapan, temuan yang menang.");
table(s, [
  ["KPI", "Draf lama", "Sekarang", "Mengapa"],
  ["Indeks biaya 2030", "96,9", `≤ ${idn0(S.clk_v2.real)} (96,9 potensi)`, "Kemerosotan harus dihentikan dulu"],
  ["Indeks biaya 2027", "102", "area pilot −60% scrap", "Penghematan pabrik datang setelah 2027"],
  ["Indeks scrap 2030", "75", idn0(S.clk_v2.scrap), "Cakupan loop dibatasi kapabilitas"],
  ["Cacat lolos 2030", "60", idn0(S.clk_v2.esc), "Loop menjangkau 40% sumber scrap"],
  ["Downtime 2030", "75", idn0(S.clk_v2.down), "Dijaga di bawah benchmark"],
  ["Know-how 2030", "83%", pct(S.clk_v2.K), "Know-how usang 10% per tahun"],
  ["Ide per engineer 2030", "4,3 diajukan", "≥ 2,4 terimplementasi", "Diukur seperti Ex.6A"],
  ["Bulan per varian 2030", "5,9", idn(S.clk_v2.months), "Kompleksitas naik dengan elektrifikasi"],
], M, 1.7, 12.1, [2.8, 2.0, 3.2, 4.1], { size: 14 });
source(s, "work/7_kpis.md §4");

(async () => {
  await pres.writeFile({ fileName: OUT });
  if (process.env.THEME_SCRIPT) {
    const { applyTheme } = require(process.env.THEME_SCRIPT);
    await applyTheme(OUT, THEME);
  }
  console.log("wrote", path.relative(ROOT, OUT));
})();
