# Stage 2 — Diagnosis Celah

> Sumber angka: `data/facts.md` (Exhibit 1–9, Exhibit 3–9 data dummy) dan `work/2_diagnosis_calc.py` (jalankan ulang: `python work/2_diagnosis_calc.py`). Angka yang memakai asumsi diberi label **[ASUMSI]**. Skor heat map adalah **penilaian tim** dengan alasan tertulis per baris.

## 0. Ringkasan satu halaman

1. **Masalahnya kecepatan, bukan hanya posisi.** Selisih biaya ke pemain baru melebar dari 6 → 12 → 17 poin indeks (2023–2025), rata-rata **+5,5 poin per tahun**. Sekitar separuh pelebaran datang dari pesaing yang makin murah, bukan dari TMMIN yang makin mahal (Exhibit 3).
2. **Mengembalikan kinerja ke level 2023 tidak cukup.** Kenaikan scrap, waktu NVA, dan downtime hanya menjelaskan sekitar **1,8–3,3 poin dari 17 poin selisih (11–19%)**. Sisanya struktural. Ini alasan kuantitatif mengapa casebook meminta solusi transformatif. **[ASUMSI: indeks nominal, porsi biaya dari model]**
3. **Mesin perbaikan TMMIN melambat.** Ide yang benar-benar diimplementasikan per engineer turun **38%** (1,08 → 0,67 per tahun), sementara waktu untuk perbaikan hanya turun 11%. Jadi masalahnya bukan hanya waktu. Setiap jam perbaikan juga makin sedikit hasilnya (−31%) (Exhibit 6A).
4. **Akar masalah:** sinyal masalah dan pelajaran perbaikan tidak punya jalur kembali, baik ke proses penyebab, ke standar bersama, maupun ke varian berikutnya. Akibatnya masalah yang sama dipecahkan berulang kali, dan laju belajar pabrik kalah dari pesaing.
5. **Area prioritas:** dua fungsi Level 1 yang menjadi "persimpangan" sinyal, yaitu **inspeksi kualitas** dan **integrasi data**. Keduanya masuk tiga besar di **27 dari 27** kombinasi bobot heat map. Titik masuk ke loop ini (sealer atau final assembly) diputuskan di Stage 4; lihat bagian 7.

---

## 1. Issue tree

**Pertanyaan kunci:** Mengapa TMMIN tidak bisa mempertahankan daya saing biaya dan kualitas di era multi-pathway, dan celah mana yang paling menentukan?

Logika MECE di level 1: selisih daya saing = **level kinerja hari ini** (cabang A, B), **biaya menambah varian di masa depan** (cabang C), dan **laju perbaikan** (cabang D). A–C mengukur posisi; D mengukur kecepatan. Cabang A dipecah persis mengikuti lima komponen biaya konversi di Exhibit 9, sehingga tidak ada tumpang tindih atau celah. Batas antara A dan B: A mengukur rupiah (termasuk biaya scrap); B mengukur cacat yang lolos ke hilir dan ke pelanggan.

```
Mengapa daya saing biaya & kualitas TMMIN tergerus?
│
├─ A. Biaya konversi per unit hari ini terlalu tinggi   (106 vs 89, Ex.3)
│   ├─ A1 Tenaga kerja ........ waktu NVA operator 20% → 22%           (Ex.4)
│   │    ├─ material flow tidak sinkron: intralogistik Level 2         (Ex.5)
│   │    └─ variasi varian ditangani operator: final assembly Level 2  (Ex.5)
│   ├─ A2 Perawatan ........... unplanned downtime 100 → 111           (Ex.4)
│   │    └─ maintenance preventif berkala, belum prediktif (Level 2)   (Ex.5)
│   ├─ A3 Scrap ............... indeks scrap 100 → 108                  (Ex.4)
│   │    ├─ cacat ditemukan di akhir: inspeksi Level 1                 (Ex.5)
│   │    └─ tidak ada umpan balik ke hulu: sealer Level 2              (Ex.5)
│   ├─ A4 Energi .............. TIDAK ADA DATA di casebook → celah data (Ex.5: data integration L1)
│   └─ A5 Depresiasi .......... utilisasi 70%, pasar −7,2%             (Ex.1, Ex.9)
│        └─ sebagian besar di luar kendali manufaktur
│
├─ B. Kualitas: cacat lolos ke proses hilir 100 → 103                 (Ex.4)
│   ├─ deteksi visual manual di akhir lini (inspeksi Level 1)          (Ex.5)
│   ├─ cek kualitas visual di painting dan press shop                  (Ex.5)
│   └─ 31% operator sering mengabaikan alert otomatis                  (Ex.6B)
│
├─ C. Biaya masa depan: setiap varian baru mahal dan lambat
│   ├─ modifikasi peralatan per varian 8 → 9 bulan                     (Ex.4)
│   ├─ peralatan point-to-point tanpa standar antarmuka (Level 2)      (Ex.5)
│   ├─ jumlah varian naik: elektrifikasi 30% → 55–70% pada 2030        (Ex.8)
│   └─ teknologi luar mahal, kapabilitas software & AI internal 2/30   (Ex.7)
│
└─ D. Laju perbaikan lebih lambat dari pesaing  (selisih +5,5 poin/tahun, Ex.3)
    ├─ D1 Waktu: engineer 62% → 65% untuk rutin; 28% → 25% untuk perbaikan (Ex.6A)
    ├─ D2 Hasil: ide/engineer 3,1 → 2,4; implementasi 35% → 28%         (Ex.6A)
    ├─ D3 Pengetahuan: know-how terdokumentasi 35% → 33%;
    │                  48% proses kritis bergantung 1–2 senior;
    │                  engineer baru mandiri 14 → 15 bulan              (Ex.6A)
    └─ D4 Kapabilitas: Software & AI Level 3+ hanya 2/30;
                       hanya 18% operator terlatih alat berbasis data   (Ex.7, Ex.6B)
```

## 2. Driver, exhibit, dan tren 2023 → 2025

| Cabang | Driver | Exhibit | 2023 | 2025 | Perubahan | Arah |
|---|---|---|---|---|---|---|
| A | Indeks biaya konversi TMMIN | 3 | 100 | 106 | +6% | Memburuk |
| A | Indeks biaya pemain baru | 3 | 94 | 89 | −5% | Pesaing membaik |
| A | Selisih biaya (poin indeks) | 3 | 6 | 17 | +11 poin | Melebar 5,5/tahun |
| A1 | Waktu NVA operator (% jam kerja) | 4 | 20% | 22% | +2 poin | Memburuk |
| A2 | Unplanned downtime (indeks) | 4 | 100 | 111 | +11% | Memburuk, terbesar |
| A3 | Scrap (indeks) | 4 | 100 | 108 | +8% | Memburuk |
| A4 | Energi | — | — | — | Tidak ada data | Celah data |
| A5 | Utilisasi Karawang I & II | 9 | — | 70% | Pasar −7,2% (Ex.1) | Tekanan eksternal |
| B | Cacat lolos ke hilir (indeks) | 4 | 100 | 103 | +3% | Memburuk |
| C | Modifikasi peralatan per varian (bulan) | 4 | 8 | 9 | +1 bulan | Memburuk |
| C | Porsi volume elektrifikasi | 8 | 30% (2026) | 55–70% (2030) | +25–40 poin | Kompleksitas naik |
| D1 | Waktu engineer untuk rutin & troubleshooting | 6A | 62% | 65% | +3 poin | Memburuk |
| D1 | Waktu engineer untuk perbaikan | 6A | 28% | 25% | −3 poin | Memburuk |
| D2 | Ide per engineer per tahun | 6A | 3,1 | 2,4 | −23% | Memburuk |
| D2 | Ide yang diimplementasikan | 6A | 35% | 28% | −7 poin | Memburuk |
| D2 | **Ide terimplementasi per engineer** (turunan) | 6A | 1,08 | 0,67 | **−38%** | Memburuk |
| D3 | Know-how kritis terdokumentasi | 6A | 35% | 33% | −2 poin | Memburuk |
| D3 | Proses kritis bergantung 1–2 senior | 6A | 45% | 48% | +3 poin | Memburuk |
| D3 | Engineer baru hingga mandiri (bulan) | 6A | 14 | 15 | +1 bulan | Memburuk |
| D4 | Engineer Software & AI Level 3+ | 7 | — | 2/30 (7%) | Snapshot | Celah terdalam |

**Pola penting:** dari 13 indikator internal TMMIN yang punya data 2023 dan 2025 (Ex.3: 1, Ex.4: 5, Ex.6A: 7), **semuanya memburuk**. Tidak ada satu pun yang membaik. Ini menandakan masalah sistemik, bukan masalah satu departemen.

## 3. Tiga temuan kuantitatif yang mengubah cara melihat kasus

### 3.1 Selisih biaya adalah masalah kecepatan

| | 2023 | 2024 | 2025 |
|---|---|---|---|
| Selisih (poin indeks) | 6 | 12 | 17 |
| TMMIN lebih mahal | 6,4% | 13,2% | 19,1% |

Pelebaran 2023–2025 berasal **52% dari biaya TMMIN yang naik** dan **48% dari biaya pemain baru yang turun** (dekomposisi logaritmik, Exhibit 3).

*Implikasi:* target yang mengejar angka 89 hari ini akan tertinggal, karena pesaing terus bergerak. Jika tren berlanjut lurus, pemain baru berada di sekitar indeks **76** pada 2030 dan selisih tanpa tindakan bisa mencapai sekitar **44 poin**. Ini **ilustrasi ekstrapolasi**, bukan prediksi.

### 3.2 Kembali ke kinerja 2023 hanya menutup 11–19% selisih

Jembatan kenaikan indeks TMMIN 100 → 106. **[ASUMSI: indeks bersifat nominal; porsi biaya tenaga kerja 40%, energi 12%, perawatan 13%, depresiasi 25%, scrap 10% sesuai `model/build_model.py`]**

| Komponen | Kontribusi (poin) | Dasar |
|---|---|---|
| Eskalasi tenaga kerja & energi 4%/tahun | +4,2 | Exhibit 9 |
| Scrap 100 → 108 | +0,8 | Exhibit 4 |
| Waktu NVA 20% → 22% (lebih banyak jam untuk output yang sama) | +1,0 | Exhibit 4 |
| Downtime 100 → 111 (jika biaya perawatan ikut 0–100%) | +0 s.d. +1,4 | Exhibit 4 |
| **Total terjelaskan** | **+6,1 s.d. +7,5** | vs teramati +6,0 |

Jembatan ini konsisten dengan data. Bagian yang bisa dikendalikan (scrap, NVA, downtime) hanya **1,8–3,3 poin**, atau 11–19% dari selisih 17 poin.

Jika pemain baru menghadapi eskalasi yang sama **[ASUMSI]**, biaya riil per unit TMMIN naik sekitar **0,8% per tahun**, sedangkan pemain baru turun sekitar **4,7% per tahun**.

*Implikasi:* "memperbaiki yang rusak" tidak akan menutup selisih. Yang harus berubah adalah **laju perbaikan tahunan** pabrik. Ini dasar data untuk visi "pabrik yang belajar lebih cepat".

### 3.3 Mesin perbaikan kehilangan waktu dan juga efektivitas

| Ukuran | 2023 | 2025 | Perubahan |
|---|---|---|---|
| Waktu engineer untuk perbaikan | 28% | 25% | −11% |
| Ide terimplementasi per engineer per tahun | 1,08 | 0,67 | −38% |
| Ide terimplementasi per poin waktu perbaikan | 0,039 | 0,027 | −31% |

*Implikasi:* membebaskan waktu engineer saja hanya memulihkan sekitar sepertiga penurunan. Dua pertiga sisanya menunjuk ke **hasil per jam perbaikan**: ide sulit diajukan (62% operator mau menyumbang bila ada kanal mudah), sulit dieksekusi (Software & AI Level 3+ hanya 2/30), dan hasilnya tidak menjadi standar (know-how terdokumentasi hanya 33%). Ini interpretasi, karena casebook tidak menjelaskan penyebab penurunan implementasi.

## 4. Gap heat map: proses × dampak

**Cara membaca:** dampak 1 = rendah, 2 = sedang, 3 = tinggi (penilaian tim). Celah maturitas = 4 − level otomasi (Exhibit 5). **Skor prioritas = (biaya + kualitas + fleksibilitas) × celah maturitas.**

| Proses | Level | Biaya | Kualitas | Fleksibilitas | Celah | **Skor** | Alasan penilaian |
|---|---|---|---|---|---|---|---|
| **Quality inspection** | 1 | 3 | 3 | 1 | 3 | **21** | Satu-satunya proses Level 1; cacat ditemukan di akhir → scrap 108 dan cacat lolos 103 |
| **Data integration** | 1 | 2 | 2 | 3 | 3 | **21** | Data peralatan, kualitas, logistik tidak terhubung; prasyarat semua loop dan setiap varian baru |
| Final assembly | 2 | 3 | 2 | 3 | 2 | 16 | Padat tenaga kerja (NVA 22%); variasi varian ditangani operator |
| Sealer | 2 | 3 | 3 | 1 | 2 | 14 | Satu-satunya proses yang disebut casebook "belum ada umpan balik kualitas otomatis" |
| Intralogistics | 2 | 3 | 1 | 2 | 2 | 12 | Forklift dan dolly manual → jalan dan menunggu (NVA) |
| Equipment & system integration | 2 | 2 | 1 | 3 | 2 | 12 | Point-to-point → penyebab langsung 9 bulan per varian |
| Casting | 2 | 2 | 2 | 1 | 2 | 10 | Finishing dan inspeksi sebagian manual |
| Maintenance | 2 | 3 | 1 | 1 | 2 | 10 | Driver dengan penurunan terbesar (downtime +11%) |
| Press shop | 3 | 2 | 2 | 2 | 1 | 6 | Ganti die dan cek panel oleh operator |
| Machining & engine assembly | 3 | 2 | 2 | 2 | 1 | 6 | Perakitan dan inspeksi sebagian manual |
| Painting | 3 | 2 | 3 | 1 | 1 | 6 | Cek dan perbaikan cacat visual manual |
| Spot welding | 3 | 1 | 1 | 2 | 1 | 4 | Robot terprogram dan terintegrasi |

**Uji ketahanan:** skor dihitung ulang untuk semua 27 kombinasi bobot (biaya, kualitas, fleksibilitas masing-masing 1, 2, atau 3).

| Proses | Masuk tiga besar |
|---|---|
| Quality inspection | 27/27 |
| Data integration | 27/27 |
| Final assembly | 21/27 |
| Sealer | 6/27 |

**Celah di antara proses** (jumlah skor proses hulu + titik tempat sinyalnya mendarat):

| Mata rantai | Skor | Loop yang terbuka |
|---|---|---|
| Final assembly → inspeksi | 37 | Kualitas |
| Sealer → inspeksi | 35 | Kualitas |
| Equipment integration → data integration | 33 | Data & peralatan |
| Maintenance → data integration | 31 | Data & peralatan |
| Intralogistics → final assembly | 28 | Aliran material |
| Painting → inspeksi | 27 | Kualitas |

**Bacaan:** dua fungsi teratas bukan proses produksi. Keduanya adalah **titik temu**: tempat sinyal kualitas seharusnya berbalik ke hulu (inspeksi) dan tempat data seharusnya mengalir antarproses (integrasi data). Ini mengonfirmasi kalimat casebook bahwa celah terbesar ada di antara proses.

## 5. Akar masalah (5-whys)

| # | Mengapa? | Jawaban | Bukti |
|---|---|---|---|
| 1 | Mengapa daya saing TMMIN tergerus? | Selisih biaya melebar 5,5 poin per tahun; pesaing membaik, TMMIN tidak | Ex.3 |
| 2 | Mengapa TMMIN tidak membaik? | Kinerja operasional memburuk di semua indikator, dan ide terimplementasi per engineer turun 38% | Ex.4, Ex.6A |
| 3 | Mengapa perbaikan tidak mengimbangi masalah? | Engineer memakai 65% waktunya untuk masalah rutin yang berulang; cacat baru terlihat di akhir lini, jauh dari penyebabnya | Ex.6A, Ex.5 |
| 4 | Mengapa masalah yang sama berulang? | Pelajaran tidak kembali. Hasil inspeksi tidak kembali ke sealer; solusi tetap di kepala senior (48%) dan coaching informal (71%); setiap varian dibangun ulang dari nol (9 bulan) | Ex.5, Ex.6A, Ex.6B, Ex.4 |
| 5 | Mengapa pelajaran tidak bisa kembali? | Tidak ada jalur balik yang dirancang: data tidak terhubung (Level 1), peralatan tanpa standar antarmuka (Level 2), tidak ada kanal ide yang mudah, dan hanya 2/30 engineer yang bisa membangun penghubungnya sendiri | Ex.5, Ex.6B, Ex.7 |

### Kalimat akar masalah

> **Pabrik TMMIN memecahkan masalah yang sama berulang kali karena sinyal masalah dan pelajaran perbaikan tidak punya jalur kembali, baik ke proses penyebab, ke standar bersama, maupun ke varian berikutnya. Akibatnya laju belajar pabrik kalah dari pesaing.**

### Uji: apakah satu kalimat ini menjelaskan ketiga komplikasi?

| Komplikasi casebook | Jalur balik yang hilang | Gejala yang dijelaskan |
|---|---|---|
| 1. Biaya & kualitas | Ke **proses penyebab** | Cacat ditemukan terlambat → scrap +8%; downtime +11% karena data peralatan tidak kembali sebagai peringatan dini |
| 2. Fleksibilitas & sumber kapabilitas | Ke **varian berikutnya** | Tiap varian dirakit ulang point-to-point → 9 bulan; integrasi bergantung pada pihak luar karena kapabilitas internal 2/30 |
| 3. Mindset, pengetahuan, talenta | Ke **standar bersama** | Know-how di kepala senior (48%) → engineer memadamkan masalah berulang (65%) → ide turun dan jarang terimplementasi (−38%) |

Kalimat ini selaras dengan "tiga loop terbuka" di draf proposal, tetapi menambahkan dimensi **kecepatan** (temuan 3.1–3.3). Dimensi ini yang menjelaskan mengapa solusi harus transformatif.

## 6. Hipotesis tandingan yang ditolak

Bagian ini penting untuk sesi Q&A, karena juri akan menguji apakah tim memilih akar masalah terlalu cepat.

| Hipotesis tandingan | Mengapa tidak menjadi akar masalah | Bukti |
|---|---|---|
| "Otomasinya kurang; beli lebih banyak robot" | Proses Level 3 tetap bermasalah di titik cek manual. Simulasi tim: kamera lebih baik di akhir lini saja menaikkan indeks scrap menjadi 112, karena cacat tetap ditemukan terlambat. Casebook sendiri menyebut teknologi luar mahal dan sulit diintegrasikan | Ex.5, `data/research.md` Tes 1 |
| "Volume turun, biaya tetap tidak terserap" | Berpengaruh pada depresiasi, tetapi pemain baru menghadapi pasar yang sama dan biayanya tetap turun. Faktor ini juga di luar pertanyaan "cara memproduksi" | Ex.1, Ex.3 |
| "Karyawan menolak perubahan" | 54% melihat teknologi sebagai pembantu dan 62% mau menyumbang ide. Yang kurang adalah pelatihan (18%) dan kanal, bukan kemauan | Ex.6B |
| "Inflasi upah dan energi" | Menjelaskan sekitar 4,2 dari 6 poin kenaikan, tetapi pesaing menghadapi tekanan serupa dan tetap turun. Yang bisa dikendalikan adalah produktivitas | Ex.9, temuan 3.2 **[ASUMSI]** |

## 7. Area prioritas dan bukti

**Area prioritas:** loop kualitas di titik deteksi, yaitu **inspeksi kualitas (Level 1) + integrasi data (Level 1)**, ditambah satu proses hulu sebagai titik masuk pilot.

| # | Bukti | Sumber |
|---|---|---|
| 1 | Hanya dua fungsi yang berada di Level 1 dari 12 proses: inspeksi dan integrasi data | Ex.5 |
| 2 | Keduanya masuk tiga besar heat map di 27/27 kombinasi bobot | Bagian 4 |
| 3 | Scrap naik 8%, sedangkan cacat lolos hanya naik 3%. Cacat makin banyak tertangkap, tetapi tertangkap terlambat. Ini pola khas loop yang terbuka | Ex.4 |
| 4 | Simulasi: menutup loop menurunkan indeks scrap area pilot 100 → 15–34; kamera saja malah 112 | `data/research.md` Tes 1 |
| 5 | Fondasi in-house sudah ada: kamera AI dari CCTV selesai divalidasi Oktober 2026 | Ex.5 |

**Catatan kritis untuk Stage 4 (pilih titik masuk):** heat map menempatkan **final assembly (16, tiga besar di 21/27 bobot)** di atas **sealer (14, 6/27)**, dan mata rantai final assembly → inspeksi (37) sedikit di atas sealer → inspeksi (35). Pilihan sealer di draf proposal tetap bisa dipertahankan, tetapi alasannya harus eksplisit dan tidak bertumpu pada skor dampak:
- Sealer adalah satu-satunya proses yang oleh casebook disebut **tidak punya umpan balik kualitas otomatis**. Celahnya paling bersih dan paling mudah diukur.
- Lingkupnya sempit dan sinyalnya jelas (bead terlewat atau tidak), sehingga pilot bisa membuktikan loop sebelum gate akhir 2027.
- Final assembly melibatkan lebih banyak operator dan variasi varian. Dampaknya lebih besar, tetapi risikonya terlalu tinggi untuk pilot pertama. Final assembly lebih tepat menjadi **gelombang rollout pertama**.

Jika tim tidak setuju dengan alasan ini, pilot final assembly → inspeksi perlu dinilai serius di Stage 4.

## 8. Peluang tersembunyi di data

| Peluang | Data | Artinya untuk solusi |
|---|---|---|
| Kolam ide yang belum tersentuh | 62% operator mau menyumbang ide bila ada kanal mudah, sementara ide per engineer turun ke 2,4 | Sumber perbaikan bisa diperluas dari engineer ke operator |
| Kemauan sudah ada, keterampilan belum | 54% melihat teknologi sebagai pembantu, tetapi hanya 18% sudah dilatih (**selisih 36 poin**) | Hambatannya pelatihan, bukan penolakan; program bisa langsung mulai dari kelompok yang sudah mau |
| Pengetahuan sudah mengalir, hanya belum tercatat | 71% know-how dibagi lewat coaching informal | Tangkap aliran yang sudah ada, bukan membuat budaya baru |
| Fondasi teknik yang kuat | Mechanical Level 3+ 63%, Electrical 50%; Software & AI hanya 7% | Pasangkan ahli domain dengan pelatihan digital yang sempit dan cepat, bukan merekrut ilmuwan data dari nol |
| Bukti kapabilitas in-house | Kamera AI dari CCTV dikembangkan sendiri | TMMIN sudah bisa membangun; tinggal menjadikannya sistem |
| Kapasitas menganggur | Utilisasi 70% → sekitar 75.000 unit/tahun kapasitas Karawang I & II belum terpakai | Varian elektrifikasi baru bisa masuk ke lini yang ada jika ganti varian cepat, tanpa pabrik baru |
| Kepercayaan operator punya nilai rupiah | Simulasi: 31% alert diabaikan → indeks scrap 34; desain berpusat manusia → 15 | Human-centered bukan sekadar slogan; itu tuas biaya yang terukur |

## 9. Implikasi untuk tahap berikutnya

| Untuk | Implikasi | Tindakan |
|---|---|---|
| Stage 3–4 | Solusi harus menaikkan **laju perbaikan**, bukan hanya memperbaiki kinerja satu kali | Tambahkan kriteria skor "meningkatkan laju belajar tahunan" |
| Stage 4 | Sealer vs final assembly sebagai titik masuk pilot | Putuskan dengan alasan di bagian 7 dan catat di slide "opsi yang ditolak" |
| Stage 5 | Model membandingkan hasil 2030 (96,9) dengan benchmark **statis** 89 (indeks yang sama di Dashboard, "54% selisih tertutup"). Juri akan bertanya: "Pesaing tidak diam, bukan?" | Laporkan dua angka: selisih tertutup terhadap 89 statis **dan** terhadap benchmark yang terus turun (ilustrasi sekitar 76). Jangan hapus angka 54%, tetapi beri konteks |
| Stage 5 | Porsi biaya konversi adalah asumsi tim dan menggerakkan semua tuas | Sudah diuji Monte Carlo (porsi tenaga kerja 35–45%); sebutkan terbuka di lampiran |
| Stage 7 | KPI laju belajar belum ada | Usulkan KPI "ide terimplementasi per engineer per tahun" (baseline 0,67) dan "poin indeks turun per tahun" |

## 10. Pertanyaan terbuka dan keterbatasan data

1. **Apakah indeks biaya (Ex.3) nominal atau riil?** Temuan 3.2 mengasumsikan nominal. Jika riil, kenaikan TMMIN 6% sepenuhnya penurunan produktivitas, dan argumen "laju perbaikan" justru makin kuat. Tanyakan ke panitia jika ada sesi klarifikasi.
2. **Porsi komponen biaya konversi** tidak diberikan casebook (hanya daftar komponennya).
3. **Data energi** tidak ada sama sekali. Ini sekaligus bukti celah integrasi data.
4. **Survei Ex.6B** hanya mencakup area pilot (N = 120). Jangan digeneralisasi ke seluruh pabrik tanpa catatan.
5. **Ex.7** memakai N = 30 per bidang. Tidak jelas apakah itu seluruh populasi engineer atau sampel.
6. Exhibit 3–9 adalah **data dummy**. Kesimpulan berlaku untuk kasus, bukan klaim tentang TMMIN yang sebenarnya.

## Cek "done when"

- [x] Satu kalimat akar masalah menjelaskan ketiga komplikasi (tabel di bagian 5).
- [x] Area prioritas didukung lebih dari dua data point (lima bukti di bagian 7).
- [x] Issue tree MECE sampai driver terukur, setiap driver punya exhibit dan tren 2023 → 2025.
- [x] Heat map proses × dampak biaya dan kualitas memakai level maturitas, dengan uji ketahanan bobot.
- [ ] **Perlu persetujuan tim:** titik masuk pilot (sealer vs final assembly) dan penambahan dimensi "laju perbaikan" ke storyline.
