# Stage 8 — Uji Panel Juri dan Bank Q&A

> Dibuat dengan skill `judge-panel`: empat sudut pandang juri, masing-masing menyerang jawaban kami sebelum juri melakukannya. Sumber angka: `work/5_tests.md` (model), `work/2_diagnosis.md` (data), dan exhibit casebook.

## 1. Serangan per sudut pandang

### Lensa 1 — Asumsi (assumption audit)

| # | Serangan | Tingkat | Bukti yang sudah ada | Perbaikan |
|---|---|---|---|---|
| 1.1 | NPV bergantung pada asumsi bahwa tanpa program kinerja terus memburuk | **Fatal** | 13 dari 13 indikator memburuk 2023–25 (Stage 2). Terhadap baseline beku 2025: NPV 2026–30 −Rp65,4 M, 2026–35 +Rp17,0 M [SD] | Tampilkan kedua baseline secara terbuka (slide 18, lampiran A4); jangan hanya menyajikan angka vs tanpa tindakan |
| 1.2 | Porsi komponen biaya konversi tidak ada di casebook | Serius | Asumsi sama di kedua model; porsi tenaga kerja diuji 35–45% (spreadsheet Monte Carlo) | Sebutkan sebagai asumsi di lampiran; usulkan klarifikasi ke panitia |
| 1.3 | Kepatuhan alert 90% terlalu optimis | Serius | Simulasi sealer: pada 31% pengabaian manfaat masih 64%; Monte Carlo SD memakai 78–95% | Kepatuhan menjadi kriteria gate (≤ 20% pengabaian) |
| 1.4 | Kalibrasi system dynamics hanya pada dua titik data dummy | Serius | Model menolak berjalan bila kalibrasi meleset > 3% | Posisikan SD sebagai pembanding kebijakan, bukan peramal; angka utama finansial dari spreadsheet |
| 1.5 | Laju akademi 30%/20% per tahun belum terbukti | Serius | Rollout di SD dibatasi jumlah engineer L3+, sehingga laju lebih lambat langsung terlihat sebagai penghematan yang lebih lambat | Peringatan dini: L3+ < 4 di akhir 2027 |

### Lensa 2 — Pasar dan pesaing (war game)

| # | Serangan | Tingkat | Bukti | Perbaikan |
|---|---|---|---|---|
| 2.1 | Pesaing terus turun; selisih tidak benar-benar tertutup | **Fatal** bila disembunyikan | Terhadap benchmark yang bergerak (ilustrasi ~76 pada 2030), selisih nominal CLK v2 37,6 poin vs 52,0 tanpa tindakan; 28% selisih dihapus [SD] | Klaim kami adalah **laju**: pelebaran selisih melambat dari 6,7 menjadi 1,7 poin per tahun (2028–30), dan pada harga konstan indeks turun ≥ 3 poin per tahun. Kami **tidak** mengklaim menutup selisih terhadap pesaing yang terus turun. Sisa selisih juga ada di luar manufaktur (utilisasi 70%, depresiasi). Disajikan terbuka di slide 18 |
| 2.2 | Porsi elektrifikasi mencapai 70% (skenario agresif) | Minor | Tornado SD: kompleksitas lebih tinggi justru menaikkan NPV (Rp20,4 M → Rp42,3 M), karena tanpa tindakan memburuk lebih cepat | Jadikan argumen: makin banyak varian, makin bernilai standar data |
| 2.3 | Volume turun lagi | Serius | Kedua model memakai volume tetap 175.000 unit (Ex.9) | Akui. Break-even hanya butuh 22% selisih tertutup, sehingga ada ruang sebelum NPV negatif |
| 2.4 | Pesaing meniru | Minor | Opsi yang mudah dibeli diberi skor rendah (Stage 4); nilai CLK ada di cara kerja dan kapabilitas | Slide 8 dan 14 |

### Lensa 3 — Eksekusi dan uang (risk and mitigation)

| # | Serangan | Tingkat | Bukti | Perbaikan |
|---|---|---|---|---|
| 3.1 | Pilot terlambat; penghematan datang setahun kemudian | **Fatal** bila tidak dijawab | P(NPV>0) turun ke 32% [XL] dan 21% [SD] | 100 hari pertama hanya dengan aset yang ada; loop sealer berjalan sebelum 31 Des 2026 (slide 16) |
| 3.2 | Melindungi waktu perbaikan membuat firefighting tidak tertangani | Serius | SD: perlindungan 35–40% memotong NPV; desain akhir melindungi norma 30% dengan kenaikan bertahap; masalah tidak tertangani memuncak sekitar 11% pada Q2 2027 | Sudah diubah di desain; peringatan dini > 15% |
| 3.3 | Gate tidak menangkap kegagalan, atau malah menghentikan program yang berhasil | Serius | Gate pertengahan 2027 menghentikan program yang berhasil; gate akhir 2027 berhenti di 22% simulasi; bila loop gagal, gate berhenti di 100% simulasi | Gate akhir 2027 dengan enam kriteria terukur (Stage 6) |
| 3.4 | Kamera AI gagal validasi Oktober 2026 | Minor | Loop tidak bergantung pada satu sensor | Andon digital dan cek operator sementara |
| 3.5 | Keuntungan hilang setelah program selesai | Serius | Program dihentikan 2031: indeks 2035 105,2 vs 98,4 [SD] | Fase 5 "Pelihara" masuk roadmap dengan anggaran penggantian teknologi |

### Lensa 4 — Cerita (narrative)

| # | Serangan | Tingkat | Bukti | Perbaikan |
|---|---|---|---|---|
| 4.1 | Dua model memberi dua angka; juri bingung | Serius | 96,9 vs 100,8; NPV 27 vs 31 | Sajikan sebagai **rentang** dengan satu kalimat alasan: system dynamics lebih konservatif karena kemerosotan harus dihentikan dulu |
| 4.2 | "Pabrik yang belajar" terdengar abstrak | Serius | Contoh sealer 5 langkah | Setiap slide konsep diikuti contoh sealer |
| 4.3 | Ringkasan eksekutif terlalu banyak angka | Minor | — | Tiga angka saja (slide 2) |
| 4.4 | Kesannya ini proyek teknologi | Minor | Teknologi saja: NPV −Rp87,8 M dan scrap naik [SD]; simulasi +12% | Slide 11–12 diletakkan sebelum angka finansial |

### Aturan tally

Serangan yang ditandai fatal oleh dua lensa atau lebih **wajib** mengubah jawaban, angka, atau roadmap:

| Serangan | Lensa yang menandai fatal | Yang sudah diubah |
|---|---|---|
| NPV hanya positif terhadap baseline yang memburuk (1.1, juga 4.1) | Asumsi, Cerita | Angka utama disajikan sebagai rentang dua model; baseline beku ditampilkan sebagai batas bawah; NPV 10 tahun vs baseline beku (+Rp17,0 M) ditambahkan |
| Kecepatan (3.1) dan pesaing yang bergerak (2.1) | Eksekusi, Pasar | Laju belajar menjadi KPI utama; benchmark bergerak ditampilkan; 100 hari pertama dan gate akhir 2027 dikunci |

Tidak ada serangan fatal yang tersisa tanpa perbaikan.

## 2. Bank Q&A (20 pertanyaan)

| # | Pertanyaan | Jawaban singkat | Bukti | Pemilik |
|---|---|---|---|---|
| 1 | Apa bedanya ini dengan membeli kamera AI dan sistem MES? | Teknologi saja menemukan cacat lebih banyak tetapi terlambat, sehingga scrap naik 12% di simulasi sealer dan indeks scrap 2030 menjadi 144 vs 131 tanpa tindakan. Yang kami ubah adalah ke mana sinyal pergi dan siapa yang bertindak. | Slide 11–12; [SIM]; [SD] | M2 |
| 2 | Mengapa mulai di sealer, bukan final assembly yang dampaknya lebih besar? | Final assembly memang skor dampaknya tertinggi, tetapi sealer satu-satunya proses yang disebut casebook tanpa umpan balik kualitas otomatis, sinyalnya paling jelas, dan kameranya sudah ada. Sealer menang di 99% kombinasi bobot; final assembly menjadi gelombang pertama 2028. | Lampiran A3; `work/4_scoring.md` §5 | M2 |
| 3 | Dari mana angka 97–101? | Spreadsheet (tuas × adopsi) memberi 96,9; model system dynamics, yang harus lebih dulu menghentikan kemerosotan, memberi 100,8. Keduanya pada harga konstan 2025, dibanding sekitar 114 bila tanpa tindakan. | Slide 2, 18; [XL]; [SD] | M3 |
| 4 | Bagaimana jika tanpa program pun kinerja TMMIN tidak memburuk? | Maka NPV 2026–30 negatif (−Rp65,4 M) dan program baru positif dalam 10 tahun (+Rp17,0 M). Tetapi 13 dari 13 indikator memburuk dalam dua tahun terakhir, jadi asumsi "tidak memburuk" bertentangan dengan data. | Lampiran A4; Stage 2 | M3 |
| 5 | Pesaing terus turun. Apakah selisih benar-benar tertutup? | Tidak pada 2030, dan kami tidak mengklaimnya. Terhadap benchmark yang terus turun, program menghapus 28% selisih dibanding tanpa tindakan, dan pelebaran selisih melambat dari 6,7 menjadi 1,7 poin per tahun. Menutup sisanya butuh gelombang perbaikan berikutnya serta tuas di luar cara memproduksi (utilisasi 70%, depresiasi). | Slide 18; [SD] | M3 |
| 6 | Mengapa tidak belanja lebih cepat bila hasilnya lebih besar? | Bila loop berhasil, belanja di awal memang lebih bernilai (P50 Rp41,8 M vs Rp20,8 M). Tetapi bila loop gagal, pilot-light menjaga P(NPV>0) di 90% vs 60%. Kami membayar premi asuransi itu secara sadar, dan boleh mempercepat setelah gate bila kriteria terlampaui. | Slide 19; [SD] | M3 |
| 7 | Apa yang terjadi jika pilot terlambat? | Ini risiko terbesar: peluang NPV positif turun ke 21–32%. Karena itu 100 hari pertama hanya memakai kamera, operator, dan team leader yang sudah ada. | Slide 16, 19 | M2 |
| 8 | Bagaimana gate bekerja dan siapa yang memutuskan? | Enam kriteria di akhir 2027, termasuk scrap pilot −60%, pengabaian alert ≤ 20%, dan ide terimplementasi ≥ 0,75 per engineer. Controller keuangan menilainya secara independen dari tim pilot; bila gagal, 75% belanja ditahan. | Slide 15, 21; `work/6_roadmap.md` §3 | M2 |
| 9 | Mengapa gate tidak lebih awal, misalnya pertengahan 2027? | Kami mengujinya: KPI orang butuh sekitar 15 bulan untuk terbaca, sehingga gate pertengahan 2027 menghentikan program yang sebenarnya berhasil (NPV 10 tahun turun dari Rp265 M ke Rp209 M). | `work/5_tests.md` §8 | M3 |
| 10 | Apakah melindungi 30% waktu engineer tidak mengganggu produksi? | Kami menguji 0–40%. Melindungi 35–40% sejak awal memang mengganggu dan memotong NPV, jadi kami melindungi norma 30%, naik bertahap dalam 6 bulan, lalu mengunci waktu yang dibebaskan loop. Tanpa perlindungan, gate salah menghentikan program di 46% simulasi (vs 22%). | Slide 13; [SD] | M1 |
| 11 | Realistiskah engineer Software & AI mahir dari 2 menjadi 14? | Laju akademi (30% L1→L2 dan 20% L2→L3 per tahun) membawa angka ke 13,6 pada 2030. Fondasi mechanical/electrical sudah kuat (63% dan 50% di L3+). Laju ini juga yang membatasi rollout di model: bila lebih lambat, penghematan ikut lambat dan terlihat di gate. | Slide 17; Ex.7; [SD] | M1 |
| 12 | Bagaimana mengubah mindset operator yang mengabaikan 31% alert? | Alert dirancang bersama team leader dan menjelaskan alasannya, setiap pengabaian dibahas di kaizen, dan 62% operator sudah mau menyumbang ide bila kanalnya mudah. Kepercayaan bernilai rupiah: dari 31% ke 10% pengabaian, manfaat scrap naik dari 64% ke 85%. | Ex.6B; [SIM] | M1 |
| 13 | Apakah program ini mengurangi tenaga kerja? | Tidak. Hanya 50% waktu operator yang dibebaskan dihitung sebagai kas; sisanya dialihkan ke kaizen dan menyerap volume. | Lampiran A2 | M1 |
| 14 | Apa dampak keberlanjutannya? | Sekitar 1.765 t CO₂ per tahun dihindari pada 2030 (15.214 t kumulatif sampai 2035), scrap −40% vs tanpa tindakan, ketergantungan pada senior turun dari 48% ke 26%. Dampak CO₂-nya kecil; manfaat lingkungan terbesar adalah material yang tidak terbuang. | Slide 20; [SD] | M3 |
| 15 | Apakah hasilnya bertahan setelah 2030? | Hanya bila cara kerja dipertahankan. Bila program dihentikan 2031, indeks 2035 naik ke 105,2 vs 98,4. Karena itu ada Fase 5 dengan anggaran penggantian teknologi sekitar Rp16 M per tahun. | Slide 20; [SD] | M2 |
| 16 | Mengapa investasi Rp80 M, bukan Rp40 M atau Rp120 M? | Rp80 M di tengah rentang casebook. Investasi adalah input paling berpengaruh di kedua tornado. Pada skenario konservatif (Rp110 M dengan tuas rendah), NPV menjadi −Rp55,4 M, dan itulah alasan gate ada. | Slide 18; tornado | M3 |
| 17 | Data Exhibit 3–9 adalah dummy. Seberapa bisa dipercaya? | Kesimpulan kami adalah mekanisme dan desain kebijakan yang tahan uji, bukan ramalan TMMIN. Setiap angka bisa dijalankan ulang dari skrip, dan model menolak berjalan bila tidak cocok dengan exhibit. | Lampiran A1 | M3 |
| 18 | Apa yang dibangun sendiri dan apa yang dibeli? | Logika loop, standar data, model AI, dan fixture dibangun sendiri karena itulah pembeda. Komputasi dan sensor khusus dari mitra, dengan transfer pengetahuan sebagai syarat pembayaran akhir. | Slide 17 | M2 |
| 19 | Bagaimana ini membantu multi-pathway (HEV, PHEV, BEV)? | Standar data mengubah varian baru menjadi konfigurasi: bulan per varian menjadi 7,2 pada 2030, dibanding 10,4 bila kompleksitas naik tanpa tindakan. Makin agresif elektrifikasi, makin bernilai programnya. | Ex.8; [SD] | M2 |
| 20 | Apa satu hal yang paling mungkin membuat ini gagal? | Kecepatan dan kepercayaan operator. Keduanya diukur sejak hari pertama dan menjadi kriteria gate. | Slide 16, 21 | M1 |

## 3. Tiga pertanyaan tersulit: jawaban lisan 20 detik

**Q4 — "Tanpa program pun mungkin tidak memburuk."**
> "Kami juga menghitung skenario itu. Bila kinerja 2025 bisa dibekukan tanpa usaha, program kami baru balik modal dalam sepuluh tahun, bukan lima. Tetapi data casebook menunjukkan ketiga belas indikator internal memburuk dalam dua tahun. Membekukan 2025 bukan pilihan yang tersedia. Pilihannya: terus merosot, atau mengubah cara pabrik belajar."

**Q5 — "Pesaing terus bergerak; selisihnya tidak tertutup."**
> "Benar, dan kami tidak mengklaim menutupnya pada 2030. Hari ini selisih melebar hampir 7 poin per tahun bila tidak ada tindakan; dengan program, pelebarannya turun ke kurang dari 2 poin. Itu langkah pertama: pabrik yang kembali belajar. Menutup sisanya butuh gelombang perbaikan berikutnya, dan tuas di luar cara memproduksi seperti utilisasi."

**Q6 — "Kalau belanja di awal lebih menguntungkan, kenapa tidak?"**
> "Karena kami belum tahu apakah loop akan berhasil di TMMIN. Bila berhasil, belanja di awal lebih untung. Bila gagal, pilot-light menjaga peluang NPV positif di 90%, sedangkan belanja di awal hanya 60%. Kami membayar premi asuransi itu secara sadar, dan gate memberi izin untuk mempercepat begitu buktinya ada."

## Cek "done when"

- [x] Tidak ada serangan fatal tanpa perbaikan.
- [x] Setiap jawaban menunjuk ke slide, exhibit, atau output model.
- [x] Tiga pertanyaan tersulit punya jawaban lisan 20 detik.
- [x] 20 pertanyaan (≥ 15).
