# Stage 5 — Uji dengan Angka

> Tiga model, tiga pertanyaan berbeda. Semua angka di bawah dikutip dari output skrip yang dijalankan ulang, bukan dari ingatan.
>
> | Model | Pertanyaan | Jalankan |
> |---|---|---|
> | **Simulasi drift sealer** (Monte Carlo diskret) | Apakah loop tertutup lebih baik daripada kamera yang lebih baik? | `cd model && python run_tests.py` |
> | **Model finansial spreadsheet** | Berapa NPV, payback, dan break-even dengan parameter Exhibit 9? | `python build_model.py && python run_tests.py` |
> | **Model system dynamics (baru)** | Bagaimana kebijakan mengubah *laju* perbaikan dari waktu ke waktu; ekonomi dan keberlanjutannya | `python sd_model.py` (sekitar 5 menit; `--quick` tanpa Monte Carlo) |
>
> Exhibit 3–9 adalah data dummy. Model system dynamics dikalibrasi ke dua titik waktu (2023 dan 2025), sehingga tugasnya membandingkan kebijakan dan memperlihatkan umpan balik, bukan meramal TMMIN sampai desimal.

## 0. Ringkasan

1. **Mekanisme terbukti di dua model:** membeli teknologi saja *memperburuk* scrap (simulasi sealer +12%; system dynamics: indeks scrap 2030 menjadi 144 vs 131 tanpa tindakan), sedangkan Closed-Loop Kaizen v2 menurunkannya ke 78.
2. **Dua model finansial saling menguatkan, dengan rentang yang jujur:** indeks biaya 2030 pada harga konstan 2025 adalah **96,9** (spreadsheet) dan **100,8** (system dynamics), dibanding **113,9** tanpa tindakan. NPV 2026–2030 adalah **Rp27,0 M** (spreadsheet) dan **Rp31,4 M** terhadap skenario tanpa tindakan (system dynamics). System dynamics lebih konservatif untuk indeks, karena program harus lebih dulu menghentikan kemerosotan.
3. **Kecepatan menentukan:** terlambat satu tahun menurunkan peluang NPV positif menjadi **32%** (spreadsheet) atau **21%** (system dynamics).
4. **Tiga temuan mengubah desain** (bagian 8): perlindungan waktu diturunkan ke norma 30% plus ratchet; gate tetap di akhir 2027, tidak dimajukan; pilot-light dipertahankan sebagai asuransi dengan premi yang kini terukur.
5. **Keberlanjutan:** sekitar 1.765 t CO₂ per tahun dihindari pada 2030; scrap (limbah material) −40% vs tanpa tindakan; ketergantungan pada 1–2 senior turun dari 48% ke sekitar 26%; hasil bertahan sampai 2035 **hanya bila cara kerja baru dipertahankan**.

---

## 1. Uji mekanisme

### 1.1 Simulasi drift sealer (diskret, 175.000 unit, 300 simulasi per skenario)

| Skenario | Scrap area pilot | Cacat lolos |
|---|---|---|
| Saat ini: inspeksi visual di akhir | indeks 100 | indeks 100 |
| Kamera lebih baik di akhir lini saja | **+11,7%** | −66,7% |
| Loop tertutup, 31% alert diabaikan (seperti hari ini) | −66,7% | −68,2% |
| Loop tertutup, desain berpusat manusia (10% diabaikan) | **−84,7%** | −86,2% |

Setiap 10 poin alert yang diabaikan menghilangkan sekitar 9 poin manfaat (0% → 93,9%; 31% → 64,3%; 50% → 49,6%). Di seluruh uji sensitivitas, penurunan scrap area pilot tidak turun di bawah sekitar 80%.

### 1.2 Model system dynamics: struktur

Model ini membuat sesuatu yang di spreadsheet hanya asumsi (kurva adopsi 10/35/65/90/100%) menjadi **hasil** dari umpan balik.

| Stok | Arti | Basis |
|---|---|---|
| Kolam masalah P | Abnormalitas berulang yang belum dipecahkan | Indeks scrap Ex.4 |
| Kapabilitas perbaikan Q | Tergerus saat waktu perbaikan di bawah norma, pulih perlahan di atasnya (*capability trap*, Repenning & Sterman 2001) | Ide terimplementasi Ex.6A |
| Know-how terdokumentasi K | Bertambah dari perbaikan dan sprint, usang 10% per tahun | Ex.6A |
| Engineer Software & AI per level | Akademi: L1→L2 30%/tahun, L2→L3 20%/tahun (sama dengan model spreadsheet) | Ex.7 |
| Kepatuhan alert operator | 69% hari ini; target 90% dengan alert yang dirancang bersama | Ex.6B |
| Cakupan loop kualitas dan standar data | Dibatasi oleh dana **dan** jumlah engineer L3+ yang bisa membangunnya | Asumsi |

Loop utama:
- **R1 jebakan firefighting:** masalah ↑ → waktu rutin ↑ → waktu perbaikan ↓ → kapabilitas ↓ → masalah ↑.
- **R2 loop belajar:** perbaikan → know-how → troubleshooting lebih cepat → waktu bebas → perbaikan.
- **R3 loop kapabilitas:** akademi → engineer L3+ → alat buatan sendiri dan rollout lebih cepat.
- **B1 kepercayaan:** alert yang bermakna → kepatuhan → cacat tertangkap di sumber.
- **B2 penyeimbang:** firefighting membersihkan gejala (80% kembali); sebagian masalah tidak bisa dihilangkan (lantai 85% dari kolam 2023); produktivitas perbaikan paling banyak naik 2× vs 2023.

**Kalibrasi** (skenario tanpa tindakan harus mereproduksi 2023 → 2025):

| Variabel | Model | Exhibit |
|---|---|---|
| Indeks scrap 2025 | 1,080 | 1,08 (Ex.4) |
| Ide terimplementasi per engineer 2025 | 0,670 | 0,67 (Ex.6A, 2,4 × 28%) |
| Know-how terdokumentasi 2025 | 33,0% | 33% (Ex.6A) |
| Waktu rutin 2025 | 65,2% | 65% (Ex.6A) |
| Bulan modifikasi varian 2025 | 9,0 | 9 (Ex.4) |
| Waktu NVA 2025 | 22,0% | 22% (Ex.4) |
| Downtime 2025 | 1,110 | 1,11 (Ex.4) |
| Indeks biaya 2024 / 2025 | 103,1 / 106,6 | 103 / 106 (Ex.3) |

Skrip menolak berjalan bila ada kalibrasi yang meleset lebih dari 3%, atau bila salah satu input Monte Carlo menggeser sejarah 2023–2025.

### 1.3 Hasil kebijakan, 2030

| Kebijakan | Indeks biaya (harga konstan 2025) | Scrap | Cacat lolos | Downtime | NVA | Bulan/varian | Waktu perbaikan | Ide/engineer | Know-how | SW&AI L3+ |
|---|---|---|---|---|---|---|---|---|---|---|
| Tanpa tindakan | 113,9 | 131 | 111 | 145 | 28% | 10,4 | 15% | 0,24 | 23% | 2 |
| Beli teknologi saja | 115,2 | **144** | 85 | 145 | 28% | 10,4 | 15% | 0,24 | 23% | 2 |
| Program SDM saja | 110,7 | 121 | 108 | 130 | 25% | 10,4 | 36% | 1,56 | 52% | 13,6 |
| CLK v1 (tanpa perlindungan waktu) | 100,9 | 79 | 73 | 90 | 17% | 7,2 | 41% | 2,85 | 64% | 13,6 |
| **CLK v2** | **100,8** | **78** | **73** | **90** | **17%** | **7,2** | **41%** | **2,95** | **64%** | **13,6** |
| CLK v2, terlambat 1 tahun | 104,7 | 97 | 85 | 110 | 21% | 8,1 | 32% | 1,53 | 52% | 10,8 |

Indeks biaya pada harga konstan 2025, sehingga nilainya sama dengan indeks Ex.3 pada 2025 (model: 106,6; Ex.3: 106). Scrap, cacat lolos, dan downtime memakai indeks 2023 = 100.

**Bacaan:**
- Teknologi saja menurunkan cacat lolos (kamera menemukan lebih banyak), tetapi scrap naik dan masalah tidak berkurang. Pabrik tetap terjebak.
- Program SDM saja membangun orang, tetapi tanpa loop sinyal masalah tetap terlambat. Indeks biaya masih di atas hari ini.
- Hanya kombinasi loop + orang yang menurunkan biaya di bawah level 2025 (106,6), dan sekitar 13 poin di bawah jalur tanpa tindakan.

## 2. Model finansial

### 2.1 Spreadsheet (angka utama deck)

Parameter Exhibit 9: 175.000 unit, Rp3,2 juta per unit (Rp560 M), diskonto 10%, umur teknologi 5 tahun, eskalasi 4%.

| Rp miliar | Konservatif | Dasar | Optimis |
|---|---|---|---|
| Investasi | 110 | 80 | 60 |
| Penghematan run-rate per tahun | 25,9 | **48,1** (8,6% biaya konversi) | 70,4 |
| NPV (10%, 2026–2030) | (55,4) | **27,0** | 102,4 |
| Payback | Setelah 2030 | **2029** | 2027 |
| Indeks biaya pada harga konstan 2025 | — | **96,9** | — |

### 2.2 System dynamics (cek silang)

| Rp miliar, CLK v2 | 2026 | 2027 | 2028 | 2029 | 2030 |
|---|---|---|---|---|---|
| Penghematan vs tanpa tindakan | 0,2 | 5,9 | 25,5 | 57,3 | 86,2 |
| Penghematan vs kinerja dibekukan di 2025 | −10,8 | −13,0 | −1,5 | 22,2 | 43,1 |
| Spreadsheet, untuk pembanding | 4,8 | 17,5 | 33,8 | 48,7 | 56,3 |
| Investasi | 8,0 | 12,0 | 32,0 | 20,0 | 8,0 |
| Biaya berjalan + pelatihan | 3,3 | 4,5 | 7,7 | 9,7 | 10,5 |

| Ukuran | Nilai |
|---|---|
| NPV 2026–2030 vs tanpa tindakan | **Rp31,4 M**; payback 2030; IRR 43% |
| NPV 2026–2030 vs kinerja dibekukan di 2025 | **−Rp65,4 M** |
| NPV 2026–2035, termasuk penggantian teknologi 1/5 per tahun setelah 2030 | Rp265,4 M vs tanpa tindakan; **Rp17,0 M vs dibekukan** |
| Penghematan 2030 | Rp86,2 M = 12,7% biaya konversi 2030 |

**Perbedaan yang harus diakui:** dalam system dynamics, penghematan datang lebih lambat. Program harus lebih dulu *menghentikan kemerosotan* sebelum bisa memotong biaya di bawah 2025. Karena itu:
- Terhadap skenario tanpa tindakan (pabrik terus merosot seperti 2023–2025), NPV positif dan dekat dengan spreadsheet.
- Terhadap baseline yang membekukan kinerja 2025 tanpa usaha, NPV 2026–2030 negatif. Program baru positif dalam horizon 10 tahun.
- Jawaban untuk juri: data 2023–2025 menunjukkan **semua 13 indikator memburuk** (Stage 2), sehingga "membekukan 2025" bukan pilihan yang tersedia tanpa program. Angka ini tetap kami tunjukkan karena merupakan batas bawah yang jujur.

### 2.3 Daya saing terhadap benchmark

| 2030, indeks nominal | Indeks | Selisih vs 89 tetap | Selisih vs benchmark turun 2,5/tahun (ilustrasi, ~76) |
|---|---|---|---|
| Tanpa tindakan | 128,5 | 39,5 | 52,0 |
| Beli teknologi saja | 129,8 | 40,8 | 53,3 |
| **CLK v2** | **114,1** | **25,1** | **37,6** |

- CLK v2 menghapus **28%** selisih 2030 terhadap benchmark yang bergerak, dibanding tanpa tindakan.
- Terhadap benchmark yang bergerak, pelebaran selisih 2028–30 melambat dari **6,7** menjadi **1,7 poin per tahun**. Program memperlambat pelebaran, tetapi **tidak menutup** selisih terhadap pesaing yang terus turun. Setelah 2031 indeks pada harga konstan mendatar di sekitar 98 (lantai masalah di model), sehingga gelombang perbaikan berikutnya tetap dibutuhkan.
- Angka "54% selisih tertutup" di spreadsheet membandingkan 96,9 (harga konstan 2025) dengan 89 yang tetap. Angka itu benar untuk definisinya, tetapi selalu disajikan bersama catatan bahwa pesaing juga bergerak.
- Jika depresiasi investasi program dibebankan ke indeks, tambahannya sekitar +3,0 poin per tahun selama umur 5 tahunnya. Indeks 96,9 tidak memasukkan biaya program; NPV memasukkannya.

## 3. Break-even (spreadsheet)

| Investasi | Penghematan tahun pertama untuk impas | Porsi selisih biaya yang harus tertutup |
|---|---|---|
| Rp80 M | Rp19,6 M/tahun | sekitar 22% |
| Rp120 M | Rp29 M/tahun | sekitar 33% |

Faktor PV untuk Rp1 penghematan tahun pertama adalah 4,08 (anuitas tumbuh 4%, diskonto 10%, 5 tahun).

## 4. Uji stres

### 4.1 Spreadsheet (10.000 simulasi, 13 input)

| Strategi | P(NPV>0) | P5 |
|---|---|---|
| Belanja di awal, tanpa gate | 49% | −Rp32,8 M |
| Pilot-light, tanpa gate | 73% | −Rp19,4 M |
| **Pilot-light + gate (rencana)** | **86%** | **−Rp8,4 M** |
| Rencana, penghematan terlambat 1 tahun | 32% | −Rp31,9 M |

Gate terpicu (adopsi < 80%) di 25% simulasi.

### 4.2 System dynamics (1.500 simulasi per strategi, 18 input segitiga)

| Strategi | P(NPV>0) 2026–30 | P5 | P50 | P95 | Gate berhenti | Ide/engineer 2030, P50 |
|---|---|---|---|---|---|---|
| **Rencana: CLK v2, pilot-light + gate** | **94%** | −1,9 | 20,8 | 40,7 | 22% | 2,7 |
| Pilot-light tanpa gate | 87% | −7,7 | 16,3 | 40,5 | — | 2,8 |
| Belanja di awal + gate | 99% | 15,3 | 41,8 | 70,8 | 22% | 3,1 |
| Belanja di awal tanpa gate | 98% | 10,4 | 40,0 | 70,9 | — | 3,1 |
| Loop gagal (adopsi 20–60%): pilot-light + gate | **90%** | **−2,3** | 9,5 | 22,5 | 100% | 1,9 |
| Loop gagal (adopsi 20–60%): belanja di awal + gate | **60%** | **−18,8** | 3,3 | 25,8 | 100% | 2,3 |
| CLK v1, tanpa perlindungan waktu + gate | 97% | 5,5 | 27,3 | 43,3 | **46%** | 2,4 |
| CLK v2, lindungi 40% + gate | 91% | −4,5 | 19,5 | 40,5 | 22% | 3,3 |
| **Rencana, terlambat 1 tahun** | **21%** | −30,0 | −11,6 | 7,1 | 23% | 1,4 |
| Beli teknologi saja | 0% | −89,5 | −87,8 | −86,1 | — | 0,2 |

Semua dalam Rp miliar, NPV 2026–2030 terhadap skenario tanpa tindakan. Grafik: `outputs/charts/fig_sd_mc.png`.

## 5. Tornado

| Spreadsheet (NPV dasar Rp27,0 M) | Rentang | System dynamics (NPV dasar Rp31,4 M) | Rentang |
|---|---|---|---|
| Investasi | −1,5 .. 46,0 | Investasi | 2,9 .. 50,5 |
| Adopsi yang tercapai | −18,0 .. 27,0 | Laju kompleksitas setelah 2025 | 20,4 .. 42,3 |
| Penurunan scrap | 7,4 .. 46,7 | Penurunan waktu NVA | 21,3 .. 40,1 |
| Proyek varian per tahun | 18,8 .. 43,4 | Penurunan biaya varian | 25,1 .. 37,8 |
| Biaya per proyek varian | 14,7 .. 39,3 | Cakupan scrap yang terjangkau loop | 25,1 .. 37,8 |
| | | Adopsi | 20,7 .. 31,4 |

**Asumsi yang harus dipertahankan di Q&A:** besar investasi, adopsi (termasuk kepercayaan operator), dan penurunan scrap/NVA. Ketiganya juga menjadi kriteria gate (Stage 6).

## 6. Benchmark per tuas

| Tuas | Benchmark eksternal | Asumsi spreadsheet (dasar) | Hasil system dynamics 2030 vs 2025 | Di bawah benchmark? |
|---|---|---|---|---|
| Scrap | Simulasi tim: −85% di area loop × 40% cakupan ≈ −34% | −35% | −27% (78 vs 108) | Ya |
| Downtime / perawatan | McKinsey: biaya −18–25%, downtime hingga −50% | Biaya −10% | Downtime −19% (90 vs 111) | Ya |
| Waktu NVA operator | Toyota AI Platform >10.000 jam/tahun; Omron AMR hingga 15 km/hari | −30% | −24% (16,8% vs 22%) | Ya |
| Energi | Nissan AS +13,8% dalam 3 tahun (8–21% per pabrik) | −5% | −5% pada cakupan penuh | Ya |
| Modifikasi varian | Virtual commissioning −70% (Wipro PARI); −40% (Kalypso) | −35% biaya | −20% bulan (7,2 vs 9) | Ya |

## 7. Keberlanjutan

### 7.1 Lingkungan

| Ukuran (CLK v2 vs tanpa tindakan) | 2030 | Kumulatif 2026–30 | Kumulatif 2026–35 |
|---|---|---|---|
| Listrik dihemat | 2.206 MWh/tahun | — | — |
| CO₂ dihindari | **1.765 t/tahun** | 3.709 t | 15.214 t |
| Nilai pajak karbon (Rp30/kg CO₂e) | Rp0,05 M/tahun | — | — |
| Indeks scrap (limbah material) | 78 vs 131 (**−40%**) | — | — |

Dasar hitungan:
- Tarif listrik PLN I-3 Rp1.114,74/kWh (2025).
- Faktor emisi grid Jawa-Madura-Bali 0,80 tCO₂/MWh (Kepmen ESDM 163.K/HK.02/MEM.S/2021, data 2019).
- **[ASUMSI]** 70% biaya energi adalah listrik grid.
- Tarif pajak karbon Rp30/kg CO₂e mengikuti UU 7/2021 (HPP).

**Kejujuran:** dampak CO₂ dari program ini kecil, dan nilai pajak karbonnya tidak material. Manfaat lingkungan terbesar adalah scrap yang tidak terjadi. Massa material yang dihindari tidak kami hitung karena casebook tidak memberi berat atau komposisi scrap.

### 7.2 Sosial (orang dan pengetahuan)

| Ukuran | Baseline (Ex.) | Tanpa tindakan 2030 | CLK v2 2030 | CLK v2 2035 |
|---|---|---|---|---|
| Engineer Software & AI L3+ | 2/30 (Ex.7) | 2 | **13,6** | 22,1 |
| Know-how kritis terdokumentasi | 33% (Ex.6A) | 23% | **64%** | 81% |
| Proses kritis bergantung 1–2 senior | 48% (Ex.6A) | 55% | **26%** | 14% |
| Engineer baru hingga mandiri | 15 bulan (Ex.6A) | — | **10,8 bulan** | 8,5 bulan |
| Waktu engineer untuk perbaikan | 25% (Ex.6A) | 15% | **41%** | 45% |
| Ide terimplementasi per engineer | 0,67 (Ex.6A) | 0,24 | **2,95** | 3,47 |

Waktu operator yang dibebaskan: hanya 50% yang dihitung sebagai kas. Sisanya dialihkan ke kaizen dan menyerap volume, tanpa PHK (asumsi yang sama dengan spreadsheet).

Ketergantungan pada senior dan waktu hingga mandiri diturunkan dari know-how dengan hubungan linear yang dikalibrasi ke Ex.6A (galat kalibrasi sekitar 1,6 poin dan 0,6 bulan).

### 7.3 Ketahanan hasil sampai 2035

| Indeks biaya pada harga konstan 2025 | 2030 | 2035 |
|---|---|---|
| CLK v2, cara kerja dipertahankan (penggantian teknologi dibiayai) | 100,8 | **98,4** |
| CLK v2, program dihentikan 2031 (standar tidak dipelihara, akademi dan perlindungan waktu berhenti) | 100,8 | **105,2** |
| Tanpa tindakan | 113,9 | 118,7 |
| Beli teknologi saja | 115,2 | 120,4 |

NPV 2026–2035 turun dari Rp265,4 M ke Rp241,4 M bila program dihentikan. **Pesan:** keuntungan tidak tersimpan di peralatan, melainkan di cara kerja. Begitu loop tidak dipelihara, sekitar 6,8 poin indeks hilang dalam lima tahun.

## 8. Temuan yang mengubah desain

| # | Temuan | Bukti | Perubahan |
|---|---|---|---|
| 1 | Melindungi 35–40% waktu engineer sejak awal memotong firefighting sebelum loop membebaskan waktu. Akibatnya ada masalah yang tidak tertangani dan NPV 2026–30 turun Rp2,6 M (lindungi 30%) sampai Rp3,6 M (lindungi 40%) dibanding v1 | Sapuan tingkat perlindungan 0–40%; Monte Carlo v1 vs v2 | Lindungi **norma 30%**, dinaikkan bertahap dalam 6 bulan, plus **ratchet**: waktu yang dibebaskan loop dikunci untuk perbaikan dan tidak dialihkan |
| 2 | Tanpa perlindungan waktu, KPI orang tertinggal dan gate menghentikan program yang sebenarnya berhasil di **46%** simulasi (v2: 22%). Peluang mencapai ide ≥2,4 per engineer pada 2030: 51% vs 65% | Monte Carlo | Perlindungan waktu dipertahankan. Nilainya adalah keandalan gate dan kapabilitas, bukan kas jangka pendek. Ini kami nyatakan terbuka |
| 3 | Gate pertengahan 2027 terlalu dini: kepatuhan alert dan ide belum terbaca, sehingga program yang berjalan baik ikut berhenti | Skenario gate pertengahan 2027: gate berhenti; NPV 2026–35 Rp208,8 M vs Rp265,4 M | Gate **tetap akhir 2027** (sekitar 15 bulan data pilot) |
| 4 | Bila belanja dikaitkan dengan cakupan, belanja di awal bernilai lebih tinggi **jika loop berhasil** (P50 Rp41,8 M vs Rp20,8 M). Bila loop gagal, pilot-light jauh lebih aman (P(NPV>0) 90% vs 60%; P5 −Rp2,3 M vs −Rp18,8 M) | Monte Carlo, termasuk uji kegagalan di luar lantai adopsi 60% | Pilot-light dipertahankan sebagai **asuransi** dengan premi yang terukur, sekitar Rp21 M median NPV. Di gate, bila kriteria terlampaui dengan jelas, belanja tahap 2 boleh dipercepat |
| 5 | Kecepatan adalah faktor penentu di kedua model | Terlambat 1 tahun: P(NPV>0) 32% (spreadsheet), 21% (system dynamics) | 100 hari pertama hanya memakai aset yang ada; loop sealer berjalan Q4 2026 |

## 9. Skenario terlemah dan jawabannya

| Skenario terlemah | Angka | Jawaban di roadmap (Stage 6) |
|---|---|---|
| Penghematan terlambat 1 tahun | P(NPV>0) 21–32% | 100 hari pertama dengan kamera CCTV tervalidasi; tidak menunggu sistem baru |
| Loop tidak berhasil (adopsi 20–60%) | P5 −Rp2,3 M dengan pilot-light | Gate akhir 2027 menghentikan 75% belanja |
| Skenario konservatif spreadsheet | NPV −Rp55,4 M | Gate mencegah skenario ini menghabiskan seluruh investasi |
| Juri berargumen "tanpa program kinerja tidak memburuk" | NPV 2026–30 −Rp65,4 M; 2026–35 +Rp17,0 M | Data menunjukkan 13 dari 13 indikator memburuk; kami tetap menunjukkan angka ini sebagai batas bawah |

## 10. Keterbatasan model system dynamics

- Kalibrasi hanya pada dua titik waktu data dummy. Elastisitas erosi kapabilitas (3,5) tinggi karena penurunan ide 38% dalam dua tahun harus dijelaskan. Monte Carlo tidak memvariasikannya karena terikat kalibrasi.
- Tidak ada guncangan peluncuran model. Karena itu nilai ratchet (mencegah waktu ditarik kembali saat krisis) tidak terlihat di angka.
- Volume tetap 175.000 unit, dan indeks diasumsikan nominal.
- Porsi komponen biaya konversi adalah asumsi yang sama dengan spreadsheet.
- Lantai masalah (85%) dan batas produktivitas (2×) adalah asumsi penahan. Tanpa keduanya, model melebih-lebihkan manfaat jauh di atas benchmark (versi awal memberi penghematan 38% biaya konversi). Batas ini sengaja dipilih agar hasil tetap di bawah benchmark.

## Cek "done when"

- [x] Setiap angka utama deck berasal dari model (spreadsheet untuk headline finansial, system dynamics untuk mekanisme, cek silang, dan keberlanjutan).
- [x] Skenario terlemah diketahui dan punya jawaban di roadmap.
- [x] Setiap tuas didukung benchmark eksternal, dengan asumsi di bawah benchmark.
