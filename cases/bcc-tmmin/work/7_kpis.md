# Stage 7 — KPI dan Dampak

> Baseline dari exhibit. Target 2030 berasal dari model: `model/build_model.py` untuk angka finansial utama, dan `model/sd_model.py` (CLK v2, skenario dasar) untuk KPI operasional, orang, dan keberlanjutan. Kolom **Gate 2027** sama persis dengan kriteria gate di Stage 6.

## 1. KPI hasil (outcome)

| KPI | Baseline | Gate 2027 (area pilot) | Pabrik 2027 (model) | Target 2030 | Tanpa tindakan 2030 | Sumber target |
|---|---|---|---|---|---|---|
| Indeks biaya konversi, harga konstan 2025 (skala Ex.3) | 106 (Ex.3) | — | 109,2 | **≤ 101** (spreadsheet: 96,9) | 113,9 | SD 100,8 sebagai target; spreadsheet sebagai potensi atas |
| **Laju belajar: perubahan indeks biaya per tahun** | +3 poin/tahun (Ex.3, 2023–25) | Berhenti naik | +0,6 (lalu turun sejak 2028) | **≤ −3 poin/tahun** (2029–30) | +1,2/tahun | SD |
| Indeks scrap (2023 = 100) | 108 (Ex.4) | **−60% di area pilot** | 117 | **78** | 131 | SD |
| Indeks cacat lolos ke hilir | 103 (Ex.4) | — | 103 | **73** | 111 | SD |
| Indeks unplanned downtime | 111 (Ex.4) | — | 126 | **90** | 145 | SD |
| Waktu NVA operator | 22% (Ex.4) | — | 24% | **17%** | 28% | SD (spreadsheet: −30% = 15,4%) |
| Bulan modifikasi peralatan per varian | 9 (Ex.4) | — | 9,3 | **7,2** | 10,4 | SD, termasuk kompleksitas yang naik (spreadsheet tanpa kenaikan kompleksitas: 5,9) |
| Selisih ke pemain baru, nominal (poin) | 17 (Ex.3) | — | — | **25 vs 89 tetap; 38 vs benchmark bergerak** | 40 / 52 | SD |

**Catatan:** pada 2027 indeks pabrik masih di atas baseline 2025, karena program baru menghentikan kemerosotan (tanpa tindakan 110,0). Inilah alasan target 2027 diukur di area pilot, bukan di seluruh pabrik.

## 2. KPI pendorong (orang, pengetahuan, adopsi)

| KPI | Baseline | Gate 2027 | Target 2030 | Sumber target |
|---|---|---|---|---|
| Operator yang mengabaikan alert | 31% (Ex.6B) | **≤ 20%** | **10%** | SD (kepatuhan 90%) |
| Adopsi pilot (alert ditindaklanjuti sesuai aturan) | — | **≥ 80%** | ≥ 90% | Gate spreadsheet |
| Waktu engineer untuk perbaikan | 25% (Ex.6A) | **≥ 30%** | **41%** | SD (draf lama: 45%) |
| Ide terimplementasi per engineer per tahun | 0,67 (Ex.6A) | **≥ 0,75** | **≥ 2,4** (median 2,7–3,0) | SD; Monte Carlo P(≥ 2,4) = 65% |
| Know-how kritis terdokumentasi | 33% (Ex.6A) | 39% | **64%** | SD (draf lama: 83%; SD mencapai 81% pada 2035) |
| Proses kritis bergantung 1–2 senior | 48% (Ex.6A) | — | **26%** | SD |
| Engineer baru hingga mandiri | 15 bulan (Ex.6A) | — | **11 bulan** | SD 10,8 (draf lama: 9) |
| Engineer Software & AI L3+ (dari 30) | 2 (Ex.7) | 4,9 | **13,6** | SD dan spreadsheet (~14) |
| Operator terlatih alat berbasis data | 18% (Ex.6B) | 50% | **90%** | Target rencana (tidak dimodelkan) |
| Cakupan loop kualitas (lini kendaraan) | 0% | 18% | **94%** | SD |
| Proses pada standar data bersama | 0% | 14% | **75%** | SD (draf lama: 80%) |

## 3. KPI keberlanjutan

| KPI | Baseline | Target 2030 | Sumber |
|---|---|---|---|
| CO₂ dihindari dari loop energi | 0 | **1.765 t/tahun** (kumulatif 3.709 t 2026–30) | SD; grid Jamali 0,80 tCO₂/MWh |
| Listrik dihemat | 0 | **2.206 MWh/tahun** | SD; tarif PLN I-3 |
| Scrap (limbah material) vs tanpa tindakan | — | **−40%** | SD |
| PHK akibat program | — | **0**: 50% waktu operator yang dibebaskan dialihkan ke kaizen | Asumsi kedua model |
| Ketahanan: indeks biaya 2035, harga konstan 2025 | — | **≤ 99** bila cara kerja dipertahankan (105 bila dihentikan) | SD |

## 4. Koreksi terhadap draf proposal

Model system dynamics mengikat KPI pada umpan balik yang sama. Delapan target lama tidak konsisten dengan model, dan **temuan model yang menang**:

| KPI | Draf lama | Konsisten dengan model | Mengapa berubah |
|---|---|---|---|
| Indeks biaya 2027 | 102 | Area pilot −60% scrap; pabrik 109,2 (harga konstan 2025) | Penghematan datang setelah kemerosotan dihentikan |
| Indeks biaya 2030 | 96,9 | ≤ 101 (spreadsheet 96,9 sebagai potensi atas) | Program harus menghentikan kemerosotan dulu |
| Indeks scrap 2030 | 75 | 78 | Cakupan loop dibatasi kapabilitas engineer |
| Cacat lolos 2030 | 60 | 73 | Loop hanya menjangkau 40% sumber scrap |
| Downtime 2030 | 75 | 90 | Penurunan downtime dijaga di bawah benchmark |
| Know-how 2030 | 83% | 64% | Know-how juga usang 10% per tahun karena varian baru |
| Ide per engineer 2030 | 4,3 (diajukan) | ≥ 2,4 terimplementasi | Diukur sebagai ide terimplementasi agar sejalan dengan Ex.6A |
| Bulan per varian 2030 | 5,9 | 7,2 | Model memasukkan kompleksitas yang naik seiring elektrifikasi (Ex.8) |

## 5. Pohon KPI: dari pendorong ke hasil

```
Laju belajar (poin indeks/tahun)
├── Biaya konversi ← scrap, downtime, NVA, energi
│   ├── Scrap ← cakupan loop × kepatuhan alert × adopsi
│   ├── Downtime ← data mesin di loop × kolam masalah
│   └── NVA ← alat buatan sendiri + aliran material
├── Bulan per varian ← cakupan standar data
└── Kolam masalah ← waktu perbaikan × kapabilitas × know-how × engineer L3+
                     (dilindungi 30% + ratchet; akademi; sprint know-how)
```

## Cek "done when"

- [x] KPI hasil dan pendorong, dengan baseline dari exhibit.
- [x] Target pilot sama dengan kriteria gate Stage 6.
- [x] Target 2030 konsisten dengan model; target lama yang tidak konsisten dikoreksi secara terbuka.
