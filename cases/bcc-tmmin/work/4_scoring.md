# Stage 4 — Skoring dan Pilihan

> Skor 1–5 adalah **penilaian tim** dan perlu disepakati ulang bersama M1–M3 sebelum dikunci. Semua angka di bawah berasal dari `python work/4_scoring.py`.

## 1. Kriteria dan bobot

| Kriteria | Bobot | Mengapa | Asal |
|---|---|---|---|
| Dampak biaya & kualitas | 20% | Outcome utama casebook | Pertanyaan kunci |
| **Menaikkan laju belajar** | **15%** | Selisih melebar 5,5 poin per tahun; kembali ke 2023 hanya menutup 11–19% | **Baru, dari Stage 2** |
| Fleksibilitas multi-pathway | 15% | Elektrifikasi 30% → 55–70%; 9 bulan per varian | Komplikasi 2 |
| Manusia & pengetahuan | 15% | Tema Human-Centered AI Kaizen | SQ2 |
| Sulit dibeli/ditiru | 10% | Keunggulan yang bisa dibeli pesaing bukan keunggulan | Komplikasi 2 |
| Layak Rp40–120 M & 2026–2030 | 15% | Batas casebook | Exhibit 9 |
| Sesuai casebook (bukan alat) | 10% | "Bukan produk atau alat" | Batasan casebook |

## 2. Skor

| Opsi | Biaya & kualitas | Laju belajar | Fleksibilitas | Manusia | Sulit ditiru | Layak | Sesuai | **Total** |
|---|---|---|---|---|---|---|---|---|
| **Closed-Loop Kaizen v2** | 5 | 5 | 4 | 5 | 5 | 3 | 5 | **4,55** |
| C Citizen AI Tools | 3 | 4 | 3 | 5 | 4 | 4 | 5 | 3,90 |
| A Closed-Loop Jidoka | 5 | 3 | 2 | 3 | 4 | 4 | 5 | 3,70 |
| D Shop-Floor O-Beya | 2 | 4 | 2 | 5 | 4 | 5 | 4 | 3,60 |
| H Firefighting Firewall | 2 | 5 | 1 | 4 | 4 | 5 | 5 | 3,55 |
| B Plug-and-Produce | 3 | 3 | 5 | 2 | 5 | 3 | 4 | 3,45 |
| I Operator Idea Engine | 2 | 4 | 1 | 5 | 3 | 5 | 4 | 3,35 |
| K Digital Skill Academy | 1 | 3 | 3 | 5 | 3 | 5 | 3 | 3,20 |
| E Simulation-First | 2 | 3 | 5 | 2 | 4 | 3 | 4 | 3,15 |
| J Learning-Rate Governance | 2 | 4 | 2 | 2 | 3 | 5 | 4 | 3,05 |
| G Predictive Maintenance | 4 | 2 | 1 | 3 | 2 | 4 | 3 | 2,80 |
| L Energy Data Loop | 2 | 2 | 1 | 2 | 3 | 5 | 4 | 2,60 |
| F Conveyor-less + AMR | 3 | 1 | 5 | 1 | 2 | 1 | 1 | 2,10 |

**Alasan skor yang paling mungkin dipertanyakan:**
- CLK v2 hanya mendapat **3 untuk kelayakan** karena lingkupnya paling luas dan butuh integrasi data lebih dulu.
- A mendapat 5 untuk biaya & kualitas karena simulasi menunjukkan scrap area pilot turun sekitar 85% (`data/research.md`). Laju belajarnya hanya 3 karena tanpa loop pengetahuan, perbaikan berhenti di satu proses.
- H mendapat 5 untuk laju belajar karena langsung membalik pola capability trap di Ex.6A, tetapi hanya 2 untuk biaya karena tidak mengubah proses secara langsung.
- F mendapat 1 untuk kesesuaian karena opsi ini persis jenis "rekomendasi alat" yang dilarang casebook.

## 3. Apakah pilihan ini tahan terhadap bobot orang lain?

**Catatan kejujuran:** opsi gabungan cenderung menang di skoring berbobot karena menggabungkan kekuatan beberapa opsi. Karena itu kami menguji tiga hal, bukan hanya satu.

| Uji | Hasil |
|---|---|
| 20.000 kombinasi bobot acak | CLK v2 menjadi #1 di **89,6%** kombinasi; H di 5,1%, D di 2,9% |
| Kelayakan CLK v2 diturunkan ke 1 (terburuk) | CLK v2 tetap 4,25, di atas opsi tunggal terbaik (C, 3,90) |
| Tanpa opsi gabungan: opsi tunggal mana yang terkuat? | C Citizen AI Tools #1 di 40,7%; A 18,7%; H 17,3%; B 17,2% |

**Bacaan:** tidak ada satu opsi tunggal yang dominan. Empat opsi (C, A, H, B) bergantian menjadi yang terbaik tergantung bobot, dan masing-masing menutup driver yang berbeda. Ini argumen yang lebih kuat untuk menggabungkannya daripada sekadar skor total yang tinggi.

## 4. Opsi yang ditolak (bahan slide "opsi yang kami tolak")

| Opsi | Mengapa kalah | Yang tetap kami ambil |
|---|---|---|
| F Lini tanpa konveyor + AMR | Padat modal (skor kelayakan 1), terbaca sebagai rekomendasi alat, tidak membangun laju belajar | Otomasi bergerak boleh masuk nanti, mengikuti standar data B |
| G Predictive maintenance sebagai program sendiri | Cakupan sempit; tidak menyentuh loop kualitas dan pengetahuan | Data mesin masuk ke loop data sebagai sinyal |
| Kamera AI di seluruh lini (varian A tanpa loop) | Simulasi: scrap naik menjadi indeks 112 karena cacat tetap ditemukan terlambat | Kamera tetap dipakai, tetapi sebagai sumber sinyal loop |
| K Pelatihan saja | Keterampilan tanpa jalur balik tidak mengubah hasil; hanya 18% operator terlatih saat ini | Akademi menjadi bagian loop manusia, belajar di pilot nyata |
| J Target laju belajar saja | Ini cara mengukur, bukan mesin perbaikan | Menjadi KPI utama program |

## 5. Pilihan area pilot

| Kriteria (bobot) | Sealer → inspeksi | Final assembly → inspeksi | Maintenance | Painting → inspeksi | Intralogistik → final assembly |
|---|---|---|---|---|---|
| Dampak, dari heat map (25%) | 4 | **5** | 3 | 3 | 3 |
| Sinyal jelas & terukur (20%) | **5** | 3 | 4 | 3 | 3 |
| Aset sudah ada (15%) | **5** (kamera AI CCTV) | 3 | 2 | 3 | 3 (uji AGV/AMR) |
| Terbukti sebelum gate 2027 (20%) | **5** | 2 | 3 | 3 | 3 |
| Risiko orang & lingkup (10%, 5 = rendah) | 4 | 2 | 4 | 4 | 3 |
| Bisa disalin (10%) | 4 | 4 | 4 | 3 | 3 |
| **Total** | **4,55** | 3,30 | 3,25 | 3,10 | 3,00 |

- Sealer → inspeksi menjadi #1 di **99%** dari 20.000 kombinasi bobot acak.
- Jika **hanya dampak** yang dihitung, final assembly yang menang. Ini konsisten dengan Stage 2. Final assembly adalah **gelombang rollout pertama** (2028), bukan pilot.

## 6. Keputusan

> **Kami memilih Closed-Loop Kaizen v2, dengan pilot di sealer → inspeksi**, karena (1) ini satu-satunya jawaban yang menaikkan laju belajar sekaligus memangkas biaya dan kualitas, dan tidak ada opsi tunggal yang cukup; (2) pilihan ini tetap #1 di hampir 90% kombinasi bobot dan bahkan bila kelayakannya diberi skor terburuk; (3) pilot sealer bisa membuktikan loop sebelum gate akhir 2027 dengan aset yang sudah dimiliki TMMIN.

## Cek "done when"

- [x] Kriteria berbobot, skor, total, peringkat.
- [x] Alasan opsi yang kalah tercatat.
- [x] Satu ide dan satu area pilot, ditulis dalam satu kalimat dengan tiga alasan.
- [ ] **Perlu persetujuan tim** atas skor dan bobot (jalankan ulang skrip setelah mengubahnya).
