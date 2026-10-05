# Ideation

## Ide terpilih: Closed-Loop Kaizen

**Satu kalimat:** Pabrik yang belajar dari dirinya sendiri. Setiap sinyal (dari kamera, sensor, atau operator) kembali ke orang yang bisa bertindak, dan setiap perbaikan menjadi standar baru.

**Kenapa ini menjawab casebook:** casebook minta "bagaimana manufaktur berubah", bukan produk atau alat. Ide ini mengubah cara kerja, alur data, dan aliran pengetahuan, sementara teknologi hanya membawa sinyal.

## Tiga loop

| Loop | Prinsip TPS | Apa yang berubah |
|---|---|---|
| Loop kualitas | Jidoka | Abnormalitas kembali ke proses penyebabnya dalam hitungan menit, dengan aturan stop, koreksi, atau eskalasi |
| Loop data & peralatan | Standardized work | Satu standar antarmuka dan data milik TMMIN; varian baru cukup dikonfigurasi, bukan dikabel ulang |
| Loop manusia & pengetahuan | Kaizen & yokoten | Alat AI buatan operator, kanal ide satu ketukan, know-how senior didokumentasikan |

## Cara kerja satu loop (contoh sealer)

1. **Deteksi:** kamera, sensor, atau operator menemukan bead sealer yang terlewat
2. **Rutekan:** standar data mengirim sinyal ke stasiun sealer dalam hitungan detik
3. **Bertindak:** operator stop, koreksi, konfirmasi
4. **Belajar:** team leader meninjau penyebab dan setiap alert yang diabaikan di kaizen harian
5. **Standarkan:** perbaikan masuk standard work dan disebar ke lini lain

Saat ini hanya langkah 1 yang sebagian ada. Langkah 2, 4, dan 5 yang hilang.

## Area pilot: sealer → inspeksi

- Cerita biaya paling jelas: bead yang terlewat ditemukan di akhir dan bisa membuat unit di-scrap
- Fondasi sudah ada: kamera AI dari CCTV selesai validasi Oktober 2026
- Menyentuh ketiga loop sekaligus

## Semua opsi yang dipertimbangkan

| # | Ide | Inti | Kekuatan | Kelemahan |
|---|---|---|---|---|
| A | Closed-Loop Jidoka | Abnormalitas dirutekan otomatis ke proses penyebab | Dampak biaya dan kualitas kuat | Butuh integrasi data dulu |
| B | Plug-and-Produce Standard | Satu standar antarmuka in-house untuk semua peralatan | Menjawab fleksibilitas multi-pathway | Cerita "manusia"-nya lemah |
| C | Citizen Kaizen AI Platform | Operator membangun alat AI sendiri, kanal ide mudah | Paling human-centered | Butuh tata kelola dan pelatihan |
| D | Shop-Floor O-Beya | Know-how senior ditangkap jadi asisten AI | Murah, cepat dipilot | Dampak biaya langsung kecil |
| E | Simulation-First Preparation | Varian baru diuji di model digital sebelum diubah fisik | Kuat untuk kecepatan varian | Butuh data andal |
| F | Lini tanpa konveyor + AMR | Tata letak fleksibel dengan mobile automation | Fleksibilitas besar | Padat modal, terlihat seperti rekomendasi alat |
| G | Autonomous Maintenance (TPM 2.0) | Operator dan maintenance mengelola kesehatan mesin | Penghematan downtime jelas | Cakupan sempit, banyak tim lain akan usul ini |
| **H** | **Gabungan A+B+C+D = Closed-Loop Kaizen** | **Satu sistem tiga loop** | **Jawaban paling utuh** | **Perlu satu diagram yang jelas** |

## Skor (1–5, bobot dalam kurung)

| Ide | Dampak biaya & kualitas (25%) | Fleksibilitas (15%) | Manusia & pengetahuan (20%) | Sulit dibeli dari luar (15%) | Layak Rp40–120 M (15%) | Sesuai casebook (10%) | **Total** |
|---|---|---|---|---|---|---|---|
| H Gabungan | 5 | 4 | 5 | 5 | 3 | 5 | **4,55** |
| A Closed-Loop Jidoka | 5 | 3 | 4 | 4 | 4 | 5 | 4,20 |
| C Citizen Kaizen | 4 | 3 | 5 | 5 | 4 | 4 | 4,20 |
| B Plug-and-Produce | 3 | 5 | 3 | 5 | 3 | 5 | 3,80 |
| D O-Beya | 2 | 3 | 5 | 4 | 5 | 4 | 3,70 |
| E Simulation-First | 3 | 5 | 3 | 4 | 4 | 4 | 3,70 |
| G TPM 2.0 | 4 | 2 | 4 | 3 | 4 | 3 | 3,45 |
| F Konveyor-less | 3 | 5 | 2 | 2 | 2 | 2 | 2,70 |

> Skor ini usulan awal. Re-score bersama tim sebelum dikunci.

## Kenapa opsi lain ditolak (untuk Q&A)

- **Kamera AI saja:** simulasi kami menunjukkan scrap justru naik 12% karena cacat tetap ditemukan terlambat
- **AGV/AMR tanpa konveyor:** padat modal dan terbaca sebagai rekomendasi alat
- **Predictive maintenance saja:** tidak menyentuh loop kualitas dan pengetahuan
- **Pelatihan saja:** sinyal tetap tidak kembali ke sumber

## Mekanisme perubahan mindset

| Mekanisme | Baseline | Target 2030 |
|---|---|---|
| Bebaskan waktu engineer | 65% waktu untuk dukungan rutin | 45% (+10.800 jam perbaikan/tahun) |
| Mudahkan ide (satu ketukan, respons 48 jam, apresiasi) | 62% operator mau berkontribusi | Ide per engineer 2,4 → 4,3/tahun |
| Tangkap know-how senior | 33% terdokumentasi | 83% terdokumentasi |

## Build vs partner

| Komponen | Pilihan |
|---|---|
| Logika loop & aturan alert | Bangun sendiri |
| Standar antarmuka & data | Bangun sendiri |
| Model inspeksi AI | Bangun sendiri |
| Peralatan & fixture standar | Bangun sendiri |
| Komputasi & cloud | Mitra |
| Sensor canggih, proses baterai | Mitra (dengan transfer pengetahuan) |

## Roadmap singkat

| Fase | Periode | Capex | Isi |
|---|---|---|---|
| Persiapan | Q4 2026 | 10% | Loop sealer di kamera CCTV, draf standar data, kanal ide |
| Pilot | 2027 | 15% | Closed loop berjalan, alat buatan operator, know-how ditangkap |
| **Gate** | **Akhir 2027** | | **Lanjut hanya jika adopsi ≥ 80% dan penghematan sesuai rencana** |
| Standardisasi | 2028 | 40% | Disalin ke 2–3 area, standar wajib untuk peralatan baru |
| Roll-out | 2029 | 25% | Seluruh lini kendaraan Karawang |
| Skala | 2030 | 10% | Pabrik mesin, perubahan varian lewat konfigurasi |
