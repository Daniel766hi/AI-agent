# Stage 8 — Storyline dan Judul Aksi

> Judul slide dibaca berurutan harus menceritakan seluruh jawaban. Setiap angka menyebut sumbernya: **[S2]** `work/2_diagnosis_calc.py`, **[XL]** `model/build_model.py` + `model/run_tests.py`, **[SD]** `model/sd_model.py`, **[SIM]** simulasi sealer di `model/run_tests.py`, **[Ex.n]** casebook. Deck: `outputs/deck_closed_loop_kaizen.pptx` (dibangun oleh `outputs/build_deck.js`).

## Ringkasan eksekutif (jawaban + tiga angka + permintaan)

**Jawaban:** TMMIN sebaiknya mengubah *cara pabrik belajar*, bukan menambah peralatan. Closed-Loop Kaizen menutup jalur balik yang hilang (ke proses penyebab, ke standar bersama, dan ke varian berikutnya), dan melindungi waktu untuk memperbaiki agar pabrik keluar dari jebakan firefighting.

**Tiga angka:**
1. **Indeks biaya konversi 2030: 97–101 pada harga konstan 2025**, dibanding sekitar 114 bila tanpa tindakan (dari 106 hari ini) [XL 96,9; SD 100,8 dan 113,9].
2. **NPV Rp27–31 miliar** dari investasi Rp80 miliar; peluang NPV positif 86–94% [XL 10.000 simulasi; SD 1.500 simulasi].
3. **Engineer Software & AI mahir dari 2 menjadi sekitar 14 dari 30; know-how terdokumentasi dari 33% menjadi 64%** [SD; Ex.6A, Ex.7].

**Permintaan:**
1. Setujui Rp8 miliar untuk pilot sealer → inspeksi mulai Q4 2026.
2. Tunjuk satu pemilik standar data pabrik.
3. Lindungi 30% waktu perbaikan dan kunci setiap jam yang dibebaskan loop.
4. Skalakan hanya lewat gate akhir 2027.

## Urutan slide dan judul aksi

| # | Bagian | Judul aksi | Bukti di slide | Pembicara |
|---|---|---|---|---|
| 1 | Hook | Pesaing menjadi 2,5 poin lebih murah setiap tahun, sementara TMMIN 3 poin lebih mahal: selisihnya melebar 5,5 poin per tahun | Ex.3; [S2] | M1 |
| 2 | Ringkasan eksekutif | Ubah cara pabrik belajar, bukan peralatannya: biaya 97–101 pada 2030 (vs 114 tanpa tindakan), NPV Rp27–31 M, dan engineer digital mahir 2 → 14 | [XL], [SD] | M1 |
| 3 | Situasi | Pasar turun 7,2% sementara porsi elektrifikasi naik dari 30% ke 55–70%: lini yang sama harus menampung lebih banyak varian dengan biaya lebih rendah | Ex.1, Ex.8 | M1 |
| 4 | Komplikasi | Ke-13 indikator internal memburuk dalam dua tahun; tidak ada satu pun yang membaik | Ex.3, Ex.4, Ex.6A; [S2] | M1 |
| 5 | Komplikasi | Kembali ke kinerja 2023 hanya menutup 11–19% selisih: masalahnya laju perbaikan, bukan kerusakan sesaat | [S2] jembatan biaya | M3 |
| 6 | Akar masalah | Pabrik memecahkan masalah yang sama berulang kali karena sinyal dan pelajaran tidak punya jalur kembali; ide terimplementasi per engineer turun 38% | Ex.5, Ex.6A, Ex.6B; 5-whys | M1 |
| 7 | Celah terbesar | Celah terbesar ada di antara proses: inspeksi dan integrasi data, dua fungsi Level 1, masuk tiga besar di 27 dari 27 kombinasi bobot | Ex.5; heat map [S2] | M2 |
| 8 | Visi 2030 | Pada 2030, keunggulan TMMIN adalah pabrik yang belajar lebih cepat daripada yang bisa ditiru pesaing | Nilai di luar biaya: kecepatan varian, pengetahuan, orang | M1 |
| 9 | Ide | Closed-Loop Kaizen: tiga loop dengan manusia di pusat, ditambah waktu perbaikan yang dilindungi dan target laju belajar | Diagram sistem | M2 |
| 10 | Cara kerja | Satu siklus di sealer: deteksi → rutekan → bertindak → belajar → standarkan. Hari ini hanya langkah pertama yang ada | Ideation, contoh sealer | M2 |
| 11 | Bukti 1 | Kamera yang lebih baik saja menaikkan scrap 12%; menutup loop memangkasnya 85% | [SIM] `fig_sim.png` | M3 |
| 12 | Bukti 2 | Dalam simulasi system dynamics, hanya Closed-Loop Kaizen yang membalik tren biaya; teknologi saja lebih buruk daripada tanpa tindakan | [SD] `fig_sd_cost.png` | M3 |
| 13 | Manusia di pusat | Waktu perbaikan naik dari 25% ke 41%, dan ketergantungan pada 1–2 senior turun dari 48% ke 26% | [SD] `fig_sd_time.png` | M1 |
| 14 | Alternatif | Tidak ada opsi tunggal yang cukup: empat opsi bergantian menang, dan gabungannya #1 di 90% kombinasi bobot | [S4] `work/4_scoring.py` | M2 |
| 15 | Roadmap | Hanya 25% investasi dikeluarkan sebelum gate akhir 2027; sisanya hanya berdasarkan bukti | Fase, pemilik, gate | M2 |
| 16 | 100 hari pertama | Seratus hari pertama hanya memakai aset yang sudah ada: kamera CCTV tervalidasi, operator, dan team leader | Rencana 100 hari | M2 |
| 17 | Kapabilitas | TMMIN membangun sendiri apa yang menjadi pembeda, dan setiap kontrak mitra wajib mentransfer pengetahuan | Akademi, build vs partner | M2 |
| 18 | Finansial | Program Rp80 M menghasilkan NPV Rp27 M (spreadsheet) sampai Rp31 M (system dynamics), dan sudah impas bila menutup 22% selisih biaya | [XL], [SD] | M3 |
| 19 | Uji stres | Kecepatan menentukan: terlambat satu tahun menurunkan peluang NPV positif ke 21–32%; pilot-light adalah asuransi bila loop gagal | [XL], [SD] `fig_sd_mc.png` | M3 |
| 20 | Keberlanjutan | Program menghindari sekitar 1.765 t CO₂ per tahun, memangkas scrap 40%, dan hasilnya bertahan selama cara kerja dipertahankan | [SD] `fig_sd_co2.png`, `fig_sd_durability.png` | M3 |
| 21 | KPI | Target pilot sekaligus kriteria gate: scrap pilot −60%, pengabaian alert ≤ 20%, ide terimplementasi ≥ 0,75 per engineer | `work/7_kpis.md` | M3 |
| 22 | Permintaan | Empat keputusan kuartal ini: Rp8 M untuk pilot, satu pemilik standar data, 30% waktu perbaikan, dan komitmen pada gate 2027 | — | M1 |
| A1 | Lampiran | Model system dynamics: stok, loop, dan kalibrasi ke Ex.4/6A | `work/5_tests.md` §1.2 | M3 |
| A2 | Lampiran | Setiap tuas berada di bawah benchmark eksternal | `work/5_tests.md` §6 | M3 |
| A3 | Lampiran | Heat map celah dan uji ketahanan bobot | `work/2_diagnosis.md` §4 | M2 |
| A4 | Lampiran | Hasil kebijakan 2030 dan uji stres lengkap | `work/5_tests.md` §1.3, §4 | M3 |
| A5 | Lampiran | Risk register | `work/6_roadmap.md` §7 | M2 |
| A6 | Lampiran | Koreksi terbuka: target yang kami turunkan setelah model system dynamics | `work/7_kpis.md` §4 | M3 |

## Cek cerita (judul dibaca berurutan)

Selisih melebar setiap tahun → semua indikator memburuk → memperbaiki yang rusak tidak cukup → akarnya jalur balik yang hilang → celahnya di antara proses → visi pabrik yang belajar → ide tiga loop plus waktu yang dilindungi → cara kerja → dua bukti → manusia di pusat → mengapa bukan opsi lain → roadmap dengan gate → 100 hari → kapabilitas → angka finansial → uji stres → keberlanjutan → KPI → permintaan.

## Pembagian waktu presentasi (asumsi 15 menit; sesuaikan dengan aturan panitia)

| Bagian | Slide | Pembicara | Menit |
|---|---|---|---|
| Hook, ringkasan, situasi, komplikasi, akar masalah | 1–8 | M1 | 4,5 |
| Ide, cara kerja, alternatif, roadmap, 100 hari, kapabilitas | 9–10, 14–17 | M2 | 4,5 |
| Bukti, finansial, uji stres, keberlanjutan, KPI | 11–13, 18–21 | M3 | 5 |
| Permintaan | 22 | M1 | 1 |

## Cek akhir

- [x] Setiap angka di ringkasan dan judul berasal dari model atau exhibit. Cek otomatis: `python work/8_tieout.py`.
- [x] Sumber dikutip (daftar pustaka di `outputs/proposal_draft.md`).
- [ ] Placeholder nama tim dan anggota diganti (sampul dan footer): **perlu diisi tim**.
- [ ] Batas slide, halaman, dan durasi dicek terhadap aturan panitia: **perlu diisi tim**, karena aturan resmi tidak ada di folder ini.
- [ ] Gladi bersih dengan pewaktu: **perlu dilakukan tim**.
