# Isi Proposal: Closed-Loop Kaizen

> **Panduan pakai.** Salin setiap bagian ke subbab yang sama di `Template_Proposal_M3C2026.docx`. Bagian bertanda **[GAMBAR]** ditempel di kotak "[Sisipkan grafik, diagram, atau gambar di sini]" memakai file PNG di `outputs/charts/`. Ganti `[Nama Tim]` dan nama anggota di sampul dan footer.
>
> **Sumber angka.** Setiap angka berasal dari casebook (Exhibit 1–9; Exhibit 3–9 data dummy) atau dari tiga model yang bisa dijalankan ulang:
> - model finansial `model/build_model.py` + `model/run_tests.py`;
> - simulasi sealer `model/run_tests.py`;
> - model system dynamics `model/sd_model.py`.
>
> Cek otomatis bahwa angka di dokumen ini cocok dengan model: `python work/8_tieout.py`.

---

## SAMPUL

- **Judul Solusi Tim:** Closed-Loop Kaizen
- **Subjudul:** Pabrik yang belajar dari dirinya sendiri, dengan orang-orang TMMIN sebagai pusatnya
- **Tim:** [Nama Tim] · [Nama Anggota 1] · [Nama Anggota 2] · [Nama Anggota 3] · [Nama Universitas]
- **Footer:** Closed-Loop Kaizen · Tim [Nama Tim] · M3C 2026

---

## RINGKASAN EKSEKUTIF

**Kalimat kunci (kotak garis oranye):**
TMMIN sebaiknya mengubah cara pabriknya belajar, bukan menambah peralatan. Dengan menutup jalur balik yang hilang dan melindungi waktu untuk memperbaiki, indeks biaya konversi dapat turun dari 106 menjadi 97–101 pada 2030 (harga konstan 2025), sementara tanpa tindakan indeks naik ke sekitar 114.

**Paragraf 1:**
Pasar mobil nasional turun 7,2% pada 2025. Dalam dua tahun, indeks biaya konversi TMMIN di Karawang naik dari 100 ke 106, sementara pemain baru turun dari 94 ke 89. Selisihnya melebar 5,5 poin setiap tahun. Ketiga belas indikator internal yang tersedia untuk 2023 dan 2025 memburuk, dan mengembalikan kinerja ke level 2023 hanya akan menutup 11–19% selisih. Masalah TMMIN bukan kerusakan sesaat, melainkan **laju perbaikan**: ide yang benar-benar diimplementasikan per engineer turun 38%, karena sinyal masalah dan pelajaran perbaikan tidak punya jalur kembali ke proses penyebab, ke standar bersama, maupun ke varian berikutnya.

**Paragraf 2:**
Gagasan kami, **Closed-Loop Kaizen**, menutup jalur itu dengan tiga loop yang menempatkan manusia di pusat:
- **loop kualitas** berbasis jidoka;
- **loop data dan peralatan** berbasis standardized work;
- **loop manusia dan pengetahuan** berbasis kaizen dan yokoten.

Ketiganya ditambah satu aturan kerja: 30% waktu engineer dilindungi untuk perbaikan, dan setiap jam yang dibebaskan loop dikunci untuk perbaikan berikutnya. Dua simulasi menunjukkan bahwa teknologi saja memperburuk keadaan:
- di simulasi sealer, kamera yang lebih baik saja menaikkan scrap 12%, sedangkan loop tertutup memangkasnya 85%;
- di model system dynamics, hanya Closed-Loop Kaizen yang membalik tren biaya.

**Tabel indikator utama:**

| Indikator utama | Saat ini | 2030 dengan program | 2030 tanpa tindakan |
|---|---|---|---|
| Indeks biaya konversi, harga konstan 2025 | 106 | 97–101 | sekitar 114 |
| Bulan modifikasi peralatan per varian baru | 9 | 7,2 | 10,4 |
| Engineer Software & AI mahir (L3+, dari 30) | 2 | sekitar 14 | 2 |
| Investasi dan NPV (10%, 2026–2030) | Rp80 miliar | NPV Rp27–31 miliar | — |

**Paragraf 3:**
Investasi dibelanjakan bertahap (*pilot-light*): hanya 25% sebelum gate go/no-go di akhir 2027. Peluang NPV positif adalah 86% dari 10.000 simulasi model finansial dan 94% dari 1.500 simulasi system dynamics. Bila loop ternyata tidak berhasil di TMMIN, desain ini menjaga peluang itu di 90%, dibanding 60% bila belanja di awal. Program juga menghindari sekitar 1.765 ton CO₂ per tahun pada 2030 dan mengurangi ketergantungan proses kritis pada satu-dua senior dari 48% menjadi 26%.

Kami meminta TMMIN memutuskan empat hal kuartal ini:
1. menyetujui Rp8 miliar untuk pilot sealer → inspeksi;
2. menunjuk satu pemilik standar data pabrik;
3. melindungi 30% waktu perbaikan;
4. menskalakan program hanya lewat gate 2027.

---

## BAB 1. PENDAHULUAN

### 1.1 Latar Belakang

Industri otomotif global sedang berubah oleh empat tren teknologi: Connected, Autonomous, Shared, dan Electric (C.A.S.E.). Di Indonesia, perubahan ini terjadi bersamaan dengan pasar domestik yang melemah serta masuknya pemain baru dengan harga agresif dan siklus peluncuran yang cepat.

PT Toyota Motor Manufacturing Indonesia (TMMIN) mengoperasikan lima fasilitas di Jakarta dan Karawang yang memproduksi kendaraan, mesin, dan komponen. Perusahaan sedang bergeser dari fokus *green manufacturing* menuju perusahaan mobilitas, sambil menyiapkan pendekatan multi-pathway yang menampung kendaraan konvensional, HEV, PHEV, dan BEV sekaligus. Periode 2026–2030 adalah jendela terbentuknya posisi kompetitif jangka panjang, sehingga solusi yang dibutuhkan bersifat transformatif, bukan perbaikan jangka pendek.

Sesuai tema besar M3C 2026, *Human-Centered AI Kaizen*, solusi tersebut harus menempatkan manusia di pusatnya. Arah ini sudah dirintis di Toyota Jepang:
- staf pabrik membangun sekitar 10.000 model AI di platform in-house;
- sistem O-Beya menyimpan pengetahuan engineer senior agar tidak hilang saat mereka pensiun.

Paper ini mengadaptasi pelajaran tersebut untuk kondisi TMMIN, dan mengujinya dengan tiga model kuantitatif.

### 1.2 Pertanyaan Kunci

*(Sudah tertulis di template, tidak perlu diubah.)*

### 1.3 Struktur Paper

| Bab | Sub-pertanyaan | Ringkasan jawaban |
|---|---|---|
| 2 | Visi manufaktur masa depan | Pabrik yang belajar lebih cepat daripada yang bisa ditiru pesaing; celah terbesar ada di antara proses, dimulai dari sealer ke inspeksi |
| 3 | Ide transformatif | Closed-Loop Kaizen: tiga loop dengan manusia di pusat, ditambah waktu perbaikan yang dilindungi; diuji dengan simulasi sealer dan system dynamics |
| 4 | Roadmap dan pengembangan kapabilitas | Lima fase dengan gate di akhir 2027, rencana 100 hari pertama, akademi engineer, dan fase pemeliharaan setelah 2030 |
| 5 | Dampak kompetitif, finansial, dan keberlanjutan | NPV Rp27–31 miliar, peluang positif 86–94%, CO₂ dan scrap turun, serta KPI hasil dan pendorong |

Seluruh angka dapat ditelusuri ke Exhibit casebook atau ke model yang dijelaskan di Lampiran. Exhibit 3–9 adalah data dummy dari panitia.

---

## BAB 2. VISI MANUFAKTUR MASA DEPAN

**Kalimat kunci bab:**
Masalah TMMIN adalah laju perbaikan yang kalah dari pesaing. Celah terbesarnya tidak berada di dalam satu proses, melainkan di antara proses: jalur balik sinyal dan pelajaran masih terbuka, dan titik mulai yang paling jelas adalah sealer ke inspeksi.

### 2.1 Situasi Saat Ini

Penjualan wholesales nasional turun 7,2% pada 2025 menjadi 803.687 unit, dan penjualan ritel turun 6,3% menjadi 833.692 unit. Dalam dua tahun, indeks biaya konversi Karawang naik dari 100 ke 106, sementara benchmark pemain baru turun dari 94 ke 89. TMMIN kini sekitar 19% lebih mahal per unit, dan selisihnya melebar dari 6 ke 12 lalu 17 poin, atau rata-rata 5,5 poin per tahun. Sekitar separuh pelebaran itu datang dari pesaing yang terus menjadi lebih murah.

**[GAMBAR] `fig_cost.png`**
Keterangan: *Gambar 2.1 Selisih biaya konversi melebar setiap tahun. Sumber: Exhibit 3.*

Pada saat yang sama, porsi kendaraan elektrifikasi (HEV, PHEV, BEV) akan naik dari 30% volume pada 2026 menjadi 55% (moderat) atau 70% (agresif) pada 2030. Lini yang sama harus menampung lebih banyak varian tanpa menambah biaya.

### 2.2 Komplikasi: Semua Indikator Memburuk

| Tekanan | Bukti, 2023 ke 2025 |
|---|---|
| Biaya dan kualitas | Indeks scrap 100 → 108; unplanned downtime 100 → 111; cacat lolos ke hilir 100 → 103; waktu non-value-added operator 20% → 22% |
| Fleksibilitas lini | Modifikasi peralatan untuk varian baru 8 → 9 bulan; peralatan lintas generasi tersambung point-to-point tanpa standar antarmuka |
| Mindset, pengetahuan, dan talenta | Waktu engineer untuk dukungan rutin 62% → 65%; waktu perbaikan 28% → 25%; ide terimplementasi per engineer 1,08 → 0,67 (−38%); hanya 2 dari 30 engineer mahir software dan AI |

Ketiga belas indikator internal yang punya data 2023 dan 2025 memburuk; tidak ada satu pun yang membaik.

Lebih penting lagi, kenaikan scrap, waktu NVA, dan downtime hanya menjelaskan 1,8–3,3 poin dari selisih 17 poin. Kembali ke kinerja 2023 hanya menutup 11–19% selisih. (Hitungan ini memakai asumsi tim tentang porsi komponen biaya, yang tidak diberikan casebook.) Yang harus berubah adalah laju perbaikan tahunan pabrik, bukan perbaikan satu kali.

### 2.3 Akar Masalah

Lima kali "mengapa" membawa ketiga komplikasi ke satu akar:

> **Pabrik TMMIN memecahkan masalah yang sama berulang kali karena sinyal masalah dan pelajaran perbaikan tidak punya jalur kembali, baik ke proses penyebab, ke standar bersama, maupun ke varian berikutnya. Akibatnya laju belajar pabrik kalah dari pesaing.**

| Jalur balik yang hilang | Apa yang terbuka saat ini | Akibatnya |
|---|---|---|
| Ke proses penyebab | Inspeksi kualitas (Level 1) tidak mengirim hasil kembali ke hulu; sealer belum punya umpan balik kualitas otomatis | Cacat ditemukan terlambat: scrap naik 8% sementara cacat lolos hanya naik 3% |
| Ke varian berikutnya | Integrasi data Level 1; peralatan point-to-point | Setiap varian baru butuh sekitar 9 bulan pengerjaan ulang |
| Ke standar bersama | 48% proses kritis bergantung pada 1–2 senior; hanya 33% know-how terdokumentasi; 71% berbagi lewat coaching informal | Engineer memadamkan masalah yang sama (65% waktu); ide terimplementasi turun 38% |

Pola terakhir dikenal sebagai *jebakan firefighting* (Repenning & Sterman, 2001): masalah yang menumpuk memakan waktu perbaikan, sehingga masalah makin banyak.

Data yang sama juga menunjukkan peluang:
- 62% operator mau menyumbang ide bila ada kanal yang mudah;
- 54% sudah melihat teknologi sebagai pembantu, tetapi baru 18% yang dilatih.

Hambatannya keterampilan dan kanal, bukan kemauan.

### 2.4 Visi 2030 dan Nilai Baru di Luar Biaya

Pada 2030, keunggulan TMMIN adalah kecepatan pabriknya belajar, sesuatu yang tidak bisa dibeli dari luar. Biaya rendah adalah hasil, bukan visinya. Nilai baru di luar biaya ada tiga:

- **Kecepatan:** varian baru siap produksi dalam sekitar 7 bulan, dibanding lebih dari 10 bulan bila kompleksitas naik tanpa tindakan.
- **Pengetahuan yang bertumbuh:** know-how kritis terdokumentasi naik dari 33% ke 64%; ketergantungan proses kritis pada 1–2 senior turun dari 48% ke 26%; engineer baru mandiri dalam sekitar 11 bulan, bukan 15.
- **Orang yang terlibat:** waktu engineer untuk perbaikan naik dari 25% ke 41%, dan ide terimplementasi per engineer naik dari 0,67 menjadi sekitar 3 per tahun.

### 2.5 Area Prioritas

Heat map proses × dampak (biaya, kualitas, fleksibilitas) × celah maturitas menempatkan dua fungsi Level 1 di puncak: **inspeksi kualitas** dan **integrasi data**. Keduanya masuk tiga besar di 27 dari 27 kombinasi bobot. Keduanya bukan proses produksi, melainkan titik temu tempat sinyal seharusnya berbalik ke hulu.

| Proses / fungsi | Level saat ini | Celah utama | Dampak ke biaya & kualitas |
|---|---|---|---|
| Inspeksi kualitas | 1 dari 4 | Inspeksi visual manual; hasil tidak kembali ke hulu | Cacat ditemukan terlambat; scrap dan cacat lolos naik |
| Integrasi data | 1 dari 4 | Data peralatan, kualitas, dan logistik belum terhubung | Sinyal tidak bisa dirutekan; varian baru butuh pengerjaan ulang |
| Sealer application | 2 dari 4 | Manual dan semi-otomatis; belum ada umpan balik kualitas otomatis | Bead yang terlewat dapat membuat unit di-scrap |

Kami memulai di **sealer → inspeksi** karena tiga alasan:
1. Satu-satunya proses yang oleh casebook disebut tanpa umpan balik kualitas otomatis.
2. Fondasinya sudah ada: kamera AI in-house dari CCTV yang selesai divalidasi Oktober 2026.
3. Pilot ini bisa membuktikan loop sebelum gate akhir 2027.

Pilihan ini menang di 99% dari 20.000 kombinasi bobot. Final assembly, yang skor dampaknya tertinggi, menjadi gelombang pertama rollout pada 2028.

---

## BAB 3. IDE TRANSFORMATIF

**Kalimat kunci bab:**
Closed-Loop Kaizen mengubah cara pabrik bekerja, bukan apa yang dibelinya: setiap sinyal kembali ke orang yang bisa bertindak, setiap perbaikan menjadi standar, dan waktu untuk memperbaiki dilindungi agar pabrik keluar dari jebakan firefighting.

### 3.1 Gambaran Gagasan

| Komponen | Prinsip TPS | Perubahan cara kerja |
|---|---|---|
| Loop kualitas | Jidoka | Setiap abnormalitas kembali ke proses penyebabnya dalam hitungan menit, dengan aturan jelas: stop, koreksi, atau eskalasi. Operator mengonfirmasi dan memperbaiki di stasiun. |
| Loop data dan peralatan | Standardized work | Satu standar antarmuka dan data milik TMMIN. Peralatan baru tinggal disambungkan; varian baru menjadi konfigurasi, bukan pengkabelan ulang. Data mesin dan energi ikut masuk ke loop. |
| Loop manusia dan pengetahuan | Kaizen dan yokoten | Alat AI buatan operator dan engineer, kanal ide satu ketukan, dan know-how senior yang terdokumentasi mengubah keahlian individu menjadi standar bersama. |
| Waktu perbaikan yang dilindungi | Kaizen time | 30% waktu engineer dan team leader dilindungi untuk perbaikan, naik bertahap dalam 6 bulan. Setiap jam yang dibebaskan loop dikunci untuk perbaikan dan tidak dialihkan ke tugas rutin baru. |
| Target laju belajar | Genka kaizen | Pabrik dikelola dengan target "poin indeks biaya turun per tahun", dilaporkan terhadap pesaing yang juga bergerak. |

Manusia tetap di pusat secara desain:
- operator mengonfirmasi dan memperbaiki;
- team leader menyetel aturan alert;
- engineer melatih dan membangun.

Teknologi hanya membawa sinyal.

**[GAMBAR] Diagram sistem (buat sendiri di PowerPoint/Canva).** Isinya:
- tiga kotak berdampingan berjudul *Loop kualitas*, *Loop data & peralatan*, dan *Loop manusia & pengetahuan*;
- satu lingkaran "Orang TMMIN" di tengah yang terhubung ke ketiganya;
- satu pita di bawahnya bertuliskan "30% waktu perbaikan dilindungi".

Keterangan: *Gambar 3.1 Closed-Loop Kaizen: tiga loop dengan manusia di pusat.*

### 3.2 Cara Kerja

Satu siklus Closed-Loop Kaizen, dengan contoh bead sealer yang terlewat:

1. **Deteksi:** kamera, sensor, atau operator menemukan bead sealer yang terlewat.
2. **Rutekan:** standar data mengirim sinyal ke stasiun sealer dalam hitungan detik.
3. **Bertindak:** operator menghentikan, mengoreksi, dan mengonfirmasi (jidoka di stasiun).
4. **Belajar:** team leader meninjau penyebab dan setiap alert yang diabaikan di kaizen harian.
5. **Standarkan:** perbaikan masuk standard work dan disebarkan ke lini lain (yokoten).

Saat ini hanya langkah 1 yang sebagian ada. Langkah 2, 4, dan 5 yang hilang, dan itulah alasan kamera saja tidak menyelesaikan masalah.

### 3.3 Bukti 1: Simulasi Sealer

Kami membangun simulasi Monte Carlo diskret untuk drift sealer: 175.000 unit per tahun dan 300 simulasi per skenario. Parameter prosesnya ilustratif; temuannya adalah mekanisme, bukan angka absolut.

**[GAMBAR] `fig_sim.png`**
Keterangan: *Gambar 3.2 Menutup loop memangkas scrap 85%; kamera saja justru menaikkannya. Sumber: simulasi tim.*

Hasilnya:
- Kamera yang lebih baik di akhir lini menemukan lebih banyak unit cacat, tetapi terlambat untuk menyelamatkannya, sehingga scrap justru naik 12%.
- Menutup loop tepat setelah sealer menghentikan drift dalam beberapa unit dan memangkas scrap 85%.
- Bila operator mengabaikan alert seperti tingkat saat ini (31%), manfaatnya turun ke 64%. Kepercayaan adalah bagian dari nilai.

### 3.4 Bukti 2: Model System Dynamics

Model finansial biasa mengasumsikan kurva adopsi. Kami ingin tahu apakah kurva itu masuk akal, sehingga kami membangun model system dynamics (stock-and-flow, langkah bulanan, 2023–2035). Model ini dikalibrasi agar skenario tanpa tindakan mereproduksi pergerakan 2023–2025 di Exhibit 4 dan 6A. Galatnya di bawah 3%, termasuk indeks biaya 103 dan 106.

Isi modelnya:
- empat loop umpan balik: jebakan firefighting, loop belajar, loop kapabilitas, dan kepercayaan operator;
- loop penyeimbang yang menahan model agar tidak melebih-lebihkan manfaat.

**[GAMBAR] `fig_sd_cost.png`**
Keterangan: *Gambar 3.3 Hanya Closed-Loop Kaizen yang membalik tren biaya; teknologi saja lebih buruk daripada tanpa tindakan. Sumber: model system dynamics tim.*

| 2030 | Indeks biaya (harga konstan 2025) | Indeks scrap | Waktu perbaikan | Know-how |
|---|---|---|---|---|
| Tanpa tindakan | 113,9 | 131 | 15% | 23% |
| Beli teknologi saja | 115,2 | 144 | 15% | 23% |
| Program SDM saja | 110,7 | 121 | 36% | 52% |
| **Closed-Loop Kaizen** | **100,8** | **78** | **41%** | **64%** |

Teknologi saja mengurangi cacat lolos, tetapi tidak mengurangi masalah. Program SDM saja membangun orang, tetapi sinyal tetap datang terlambat. Hanya kombinasi keduanya yang menurunkan biaya di bawah level 2025.

Gagasan ini juga didukung preseden publik. Platform AI in-house Toyota di Jepang dipakai staf pabrik untuk membangun model inspeksi dan deteksi abnormalitas, dan menghemat lebih dari 10.000 jam kerja per tahun.

### 3.5 Manusia sebagai Pusat: Mindset dan Pengetahuan

Pola pikir berubah ketika waktu, kanal, dan pengakuan berubah, bukan hanya lewat pelatihan.

| Mekanisme | Baseline | 2030 (model) |
|---|---|---|
| **Lindungi waktu:** 30% untuk perbaikan, ditambah waktu yang dibebaskan loop | 25% waktu engineer untuk perbaikan | 41% |
| **Mudahkan ide:** kanal satu ketukan, respons 48 jam, apresiasi di rapat tim | 0,67 ide terimplementasi per engineer per tahun | Sekitar 3 |
| **Tangkap know-how:** sprint dengan senior, wawancara berbantuan AI yang divalidasi ahli, ditautkan ke standard work | 33% terdokumentasi; 48% proses bergantung pada 1–2 senior | 64%; 26% |

**[GAMBAR] `fig_sd_time.png`**
Keterangan: *Gambar 3.4 Waktu engineer untuk perbaikan: keluar dari jebakan firefighting. Sumber: model system dynamics tim.*

Model juga mengoreksi desain awal kami. Melindungi 35–40% waktu sejak awal mengambil waktu dari firefighting sebelum loop membebaskannya, dan menurunkan NPV. Karena itu kami melindungi norma 30%, lalu mengunci waktu yang dibebaskan loop. Tanpa perlindungan sama sekali, KPI orang tertinggal dan gate salah menghentikan program yang berhasil di 46% simulasi, dibanding 22% dengan perlindungan.

**Tabel peran (isi tabel template):**

| Peran | Saat ini | Dengan gagasan tim |
|---|---|---|
| Operator | Mengecek sealer secara visual; tahu ada miss berjam-jam kemudian | Menerima alert beberapa detik setelah miss, memperbaiki di stasiun, mencatat ide dengan satu ketukan |
| Team leader | Eskalasi dengan berjalan dan telepon; alert yang terlalu sering diabaikan | Mengelola satu papan abnormalitas; menyetel aturan alert bersama tim |
| Engineer | 65% waktu untuk dukungan rutin; engineer baru butuh 15 bulan untuk mandiri | Membangun standar dan alat; 41% waktu untuk perbaikan; engineer baru mandiri dalam sekitar 11 bulan |

### 3.6 In-house dan Kemitraan

Prinsipnya: bangun sendiri yang menjadi pembeda dan yang nilainya bertumbuh bila dimiliki; bermitra hanya untuk komoditas atau teknologi yang benar-benar khusus.

| Komponen | Pilihan | Alasan |
|---|---|---|
| Logika loop dan aturan alert | Bangun | Know-how inti, terikat ke standard work |
| Standar antarmuka dan data pabrik | Bangun | Kepemilikan inilah yang memangkas bulan per varian |
| Model inspeksi AI | Bangun | Melanjutkan kamera CCTV in-house |
| Peralatan dan fixture standar | Bangun | Lebih murah, fleksibel, memakai engineer sendiri |
| Komputasi dan cloud | Mitra | Komoditas, bukan pembeda |
| Pembangunan loop pertama di pilot | Mitra, sementara | Setelah pilot, laju rollout bergantung pada engineer L3+ sendiri |
| Sensor canggih, teknologi proses baterai | Mitra | Teknologi khusus |

Setiap kontrak mitra mewajibkan:
- engineer TMMIN berpasangan dengan engineer mitra;
- dokumentasi dalam standar TMMIN;
- serah terima sebagai syarat pembayaran akhir.

### 3.7 Alternatif yang Dipertimbangkan

Kami menilai 12 opsi dengan tujuh kriteria berbobot, termasuk "menaikkan laju belajar". Hasil uji ketahanan:
- Gabungan yang menjadi Closed-Loop Kaizen menempati peringkat pertama di sekitar 90% dari 20.000 kombinasi bobot acak, dan tetap di atas meski skor kelayakannya diberi nilai terburuk.
- Tanpa opsi gabungan, empat opsi tunggal bergantian menang. Artinya tidak ada satu opsi pun yang cukup sendirian.

| Opsi | Mengapa gagal bila berdiri sendiri |
|---|---|
| Kamera AI di seluruh lini | Menemukan cacat terlambat: scrap +12% (simulasi sealer); NPV −Rp87,8 miliar dan peluang positif 0% (system dynamics) |
| Lini tanpa konveyor dengan AGV/AMR | Padat modal, jawaban berbasis peralatan, sulit masuk rentang Rp40–120 miliar |
| Predictive maintenance saja | Tidak menyentuh loop kualitas dan pengetahuan |
| Program SDM saja | Membangun orang tetapi sinyal tetap terlambat; indeks biaya 2030 masih 110,7 |

---

## BAB 4. ROADMAP DAN PENGEMBANGAN KAPABILITAS

**Kalimat kunci bab:**
Kami bergerak cepat tetapi belanja sedikit sebelum terbukti: hanya 25% investasi dikeluarkan sebelum gate di akhir 2027, karena kedua model menunjukkan bahwa keterlambatan adalah risiko terbesar dan pilot-light adalah asuransi bila loop gagal.

### 4.1 Tahapan Implementasi 2026–2030

| Fase | Periode | Kegiatan utama | Investasi | Pemilik | Kriteria lanjut |
|---|---|---|---|---|---|
| Persiapan | Q4 2026 | Loop sealer di kamera CCTV; draf standar data; kanal ide; aturan waktu 30%; kohort akademi 1 | 10% (Rp8 M) | Manajer Body Shop | Loop berjalan sebelum 31 Desember 2026 |
| Pilot | 2027 | Loop di semua shift; 3 alat buatan sendiri; 20 item know-how ditangkap | 15% (Rp12 M) | Manajer Body Shop + pemilik standar data | **Gate akhir 2027** |
| Standardisasi | 2028 | Yokoten ke final assembly dan painting; standar data wajib untuk peralatan baru | 40% (Rp32 M) | Kepala Production Engineering | Standar terbukti di ≥ 2 area |
| Roll-out | 2029 | Seluruh lini kendaraan Karawang I & II; retrofit sesuai prioritas | 25% (Rp20 M) | Kepala Production Engineering | Kepatuhan alert ≥ 85% di semua lini |
| Skala | 2030 | Pabrik mesin; perubahan varian lewat konfigurasi | 10% (Rp8 M) | Kepala Production Engineering | Target KPI 2030 |
| Pelihara | 2031+ | Audit standar tahunan; penggantian teknologi sekitar Rp16 M/tahun; akademi mandiri | — | Direktur Produksi | Waktu perbaikan tetap ≥ 40% |

**Gate akhir 2027.** Program diskalakan hanya bila keenam kriteria terpenuhi:
1. scrap di area pilot turun ≥ 60%;
2. pengabaian alert ≤ 20%;
3. adopsi pilot ≥ 80%;
4. loop berjalan di semua shift dan area kedua siap;
5. ide terimplementasi ≥ 0,75 per engineer per tahun;
6. waktu perbaikan ≥ 30%.

Controller keuangan pabrik menilai bukti secara independen. Bila gate gagal, pilot tetap berjalan tetapi 75% belanja ditahan.

Kami juga menguji gate pertengahan 2027. Gate itu terlalu dini: KPI orang belum terbaca, sehingga program yang berhasil ikut berhenti.

**[GAMBAR] Timeline roadmap (buat sendiri).** Lima kotak berurutan:
- Persiapan (Q4 2026, 10%);
- Pilot (2027, 15%);
- Standardisasi (2028, 40%);
- Roll-out (2029, 25%);
- Skala (2030, 10%).

Tambahkan belah ketupat "Gate akhir 2027" di antara Pilot dan Standardisasi, dan satu panah "Pelihara 2031+" di ujung.
Keterangan: *Gambar 4.1 Hanya seperempat investasi dikeluarkan sebelum gate 2027.*

**Seratus hari pertama** hanya memakai apa yang sudah dimiliki TMMIN: kamera CCTV yang tervalidasi, operator, dan team leader.

| Hari | Fokus | Aksi |
|---|---|---|
| 1–30 | Lihat | Genchi genbutsu di sealer → inspeksi bersama operator; baseline scrap, cacat lolos, dan alert yang diabaikan; tunjuk pemilik standar data; luncurkan kanal ide; umumkan aturan waktu 30% |
| 31–60 | Hubungkan | Sambungkan kamera tervalidasi ke alert sealer dan andon digital; rancang aturan alert bersama team leader; sprint pertama penangkapan know-how |
| 61–100 | Jalankan | Loop berjalan di satu shift, lalu semua shift; kaizen mingguan untuk setiap alert yang diabaikan; kohort akademi pertama membangun alat pertamanya |

Kecepatan pilot sangat menentukan: bila penghematan terlambat satu tahun, peluang NPV positif turun ke 32% (model finansial) atau 21% (system dynamics).

### 4.2 Pengembangan Talenta dan Pengetahuan

Engineer software dan AI yang mahir (level 3 ke atas) naik dari 2 menjadi sekitar 14 dari 30 pada 2030. Program ini dibangun di atas kekuatan TMMIN yang sudah ada di bidang mekanikal (63% di L3+) dan elektrikal (50%).

**[GAMBAR] `fig_capability.png`**
Keterangan: *Gambar 4.2 Jumlah engineer di level 3 ke atas. Sumber: Exhibit 7 dan model kapabilitas tim.*

- **Kohort berjenjang:** 30% engineer Level 1 dan 20% engineer Level 2 naik level setiap tahun (asumsi tim, diuji di pilot). Laju ini juga membatasi kecepatan rollout di model system dynamics.
- **Belajar di pilot:** setiap kohort membangun satu alat nyata untuk lini.
- **Mengajar kembali:** engineer Level 3 menjadi pelatih mulai 2029.
- **Operator juga:** pelatihan alat berbasis data naik dari 18% menjadi 50% (2027) dan 90% (2030).
- **Penangkapan pengetahuan:** know-how kritis didokumentasikan lewat sprint terjadwal dengan senior, divalidasi ahli, dan ditautkan ke standard work. Model memperhitungkan bahwa 10% know-how menjadi usang setiap tahun karena varian baru, sehingga targetnya 64% pada 2030, bukan mendekati 100%.

### 4.3 Kolaborasi dengan Mitra

Mitra hanya dilibatkan ketika menambah nilai yang khas, seperti sensor canggih, teknologi proses baterai, dan pembangunan loop pertama selama pilot. Logika loop, standar data, dan model AI tetap in-house. Program dipimpin satu sponsor (Direktur Produksi) dan satu pemilik program (Kepala Production Engineering), dengan pemilik standar data dan forum kaizen mingguan di area pilot.

### 4.4 Risiko dan Mitigasi

| Risiko | Peluang (1–5) | Dampak (1–5) | Mitigasi | Indikator peringatan |
|---|---|---|---|---|
| Operator tidak percaya atau mengabaikan alert | 4 | 5 | Alert dirancang bersama team leader dan menjelaskan alasannya; setiap pengabaian ditinjau di kaizen | Tingkat pengabaian alert (31% saat ini) |
| Penghematan datang terlambat | 3 | 5 | Mulai dari kamera CCTV yang ada; rencana 100 hari; tinjauan KPI mingguan | Loop belum berjalan 31 Desember 2026 |
| Rollout tertahan karena engineer L3+ kurang | 4 | 4 | Akademi mulai Q4 2026; mitra untuk pilot dengan transfer pengetahuan | L3+ < 4 di akhir 2027 |
| Integrasi peralatan lama sulit | 4 | 4 | Standar wajib untuk peralatan baru; retrofit bertahap | Porsi peralatan pilot pada standar |
| Kinerja memburuk dulu sebelum membaik | 3 | 3 | Perlindungan waktu hanya 30% dan naik bertahap | Masalah tidak tertangani > 15% |
| Keuntungan hilang setelah 2030 | 3 | 4 | Fase pemeliharaan dengan anggaran penggantian teknologi | Waktu perbaikan < 40% |
| Kamera AI gagal validasi Oktober 2026 | 2 | 4 | Andon digital dan cek operator selama model dilatih ulang | Akurasi validasi terhadap ambang |

---

## BAB 5. DAMPAK KOMPETITIF, FINANSIAL, DAN KEBERLANJUTAN

**Kalimat kunci bab:**
Program Rp80 miliar menghasilkan NPV Rp27–31 miliar pada tingkat diskonto 10% dengan peluang positif 86–94%. Program sudah impas bila hanya menutup 22% selisih biaya. Hasilnya bertahan selama cara kerja baru dipertahankan.

### 5.1 Dampak pada Biaya, Kualitas, Waktu, Fleksibilitas, dan Kapabilitas

| Dimensi | Indikator | Saat ini | 2030 dengan program | 2030 tanpa tindakan |
|---|---|---|---|---|
| Biaya | Indeks biaya konversi, harga konstan 2025 | 106 | 97–101 | 113,9 |
| Kualitas | Indeks scrap (2023 = 100) | 108 | 78 | 131 |
| Kualitas | Indeks cacat lolos | 103 | 73 | 111 |
| Waktu | Bulan modifikasi peralatan per varian | 9 | 7,2 | 10,4 |
| Fleksibilitas | Proses pada standar data bersama | 0% | 75% | 0% |
| Kapabilitas SDM | Engineer software & AI L3+ (dari 30) | 2 | 13,6 | 2 |

Rentang biaya 97–101 berasal dari dua model:
- **Model finansial: 96,9.** Tuas penghematan dikalikan kurva adopsi.
- **Model system dynamics: 100,8.** Lebih konservatif, karena program harus lebih dulu menghentikan kemerosotan.

Terhadap pesaing yang terus menjadi lebih murah (ilustrasi: turun 2,5 poin per tahun), program menghapus 28% selisih 2030 dibanding tanpa tindakan, dan memperlambat pelebaran selisih dari 6,7 menjadi 1,7 poin per tahun. Program **tidak** menutup seluruh selisih pada 2030. Sisa selisih juga dipengaruhi utilisasi (70%) dan depresiasi, yang berada di luar cara memproduksi.

### 5.2 Kebutuhan Investasi dan Analisis Finansial

Pada kapasitas penuh, model finansial menghitung penghematan Rp48,1 miliar per tahun, atau 8,6% dari biaya konversi Karawang sebesar Rp560 miliar (175.000 unit × Rp3,2 juta).

| Rp miliar | Konservatif | Dasar | Optimis |
|---|---|---|---|
| Investasi | 110 | 80 | 60 |
| Penghematan per tahun (kapasitas penuh) | 25,9 | 48,1 | 70,4 |
| NPV (10%, 2026–2030) | (55,4) | 27,0 | 102,4 |
| Payback | Setelah 2030 | 2029 | 2027 |

**[GAMBAR] `fig_savings.png`**
Keterangan: *Gambar 5.1 Penghematan bruto per tuas, skenario dasar. Sumber: model finansial tim berdasarkan Exhibit 9.*

**Cek silang system dynamics.** Model system dynamics menghitung NPV Rp31,4 miliar terhadap skenario tanpa tindakan, dengan payback 2030 dan penghematan 2030 sebesar Rp86,2 miliar. Dua catatan jujur:
- Penghematan datang lebih lambat daripada di model finansial.
- Bila diasumsikan TMMIN bisa membekukan kinerja 2025 tanpa usaha, NPV 2026–2030 menjadi negatif (−Rp65,4 miliar) dan program baru positif dalam horizon 10 tahun (Rp17,0 miliar, termasuk penggantian teknologi). Kami menyajikan angka ini sebagai batas bawah, walaupun data 2023–2025 menunjukkan semua indikator memburuk.

**Break-even.** Untuk impas, investasi Rp80 miliar membutuhkan penghematan tahun pertama Rp19,6 miliar, atau sekitar 22% dari selisih biaya dengan pemain baru.

### 5.3 Uji Stres

| Strategi | P(NPV>0), model finansial (10.000 simulasi) | P(NPV>0), system dynamics (1.500 simulasi) |
|---|---|---|
| Belanja di awal, tanpa gate | 49% | 98% |
| Pilot-light, tanpa gate | 73% | 87% |
| **Pilot-light + gate (rencana)** | **86%** | **94%** |
| Rencana, terlambat 1 tahun | 32% | 21% |
| Loop gagal (adopsi 20–60%): pilot-light + gate | — | 90% |
| Loop gagal (adopsi 20–60%): belanja di awal + gate | — | 60% |

**[GAMBAR] `fig_sd_mc.png`**
Keterangan: *Gambar 5.2 Sebaran NPV per strategi: kecepatan menentukan, pilot-light adalah asuransi. Sumber: model system dynamics tim.*

Kedua model sepakat bahwa **kecepatan menentukan**. Keduanya berbeda soal belanja di awal:
- Model finansial mengasumsikan penghematan tidak dipercepat oleh belanja yang lebih awal.
- Model system dynamics mengaitkan cakupan loop dengan belanja, sehingga belanja di awal bernilai lebih tinggi **bila loop berhasil**.

Bila loop gagal, pilot-light menjaga peluang NPV positif di 90% dibanding 60%. Kami memilih pilot-light dengan sadar sebagai asuransi, dan gate memberi izin untuk mempercepat begitu buktinya ada.

Input yang paling menggerakkan NPV di kedua model adalah besar investasi, adopsi (termasuk kepercayaan operator), dan penurunan scrap serta waktu NVA. Ketiganya menjadi kriteria gate.

### 5.4 Keberlanjutan

| Dimensi | Indikator (2030, vs tanpa tindakan) | Nilai |
|---|---|---|
| Lingkungan | CO₂ dihindari dari loop energi | 1.765 ton/tahun (15.214 ton kumulatif 2026–2035) |
| Lingkungan | Listrik dihemat | 2.206 MWh/tahun |
| Lingkungan | Scrap (material terbuang) | −40% |
| Sosial | Proses kritis bergantung pada 1–2 senior | 48% → 26% |
| Sosial | Engineer software & AI mahir | 2 → 13,6 |
| Sosial | PHK akibat program | Nol: 50% waktu operator yang dibebaskan dialihkan ke kaizen |
| Ketahanan | Indeks biaya 2035, harga konstan 2025 | 98,4 bila cara kerja dipertahankan; 105,2 bila program dihentikan 2031 |

Dasar hitungan emisi:
- tarif listrik PLN golongan I-3 (Rp1.114,74/kWh);
- faktor emisi grid Jawa-Madura-Bali 0,80 tCO₂/MWh;
- asumsi tim bahwa 70% biaya energi adalah listrik.

Dampak CO₂-nya kecil, dan nilainya pada tarif pajak karbon Rp30/kg tidak material. Manfaat lingkungan terbesar adalah material yang tidak lagi terbuang menjadi scrap.

**[GAMBAR] `fig_sd_durability.png`**
Keterangan: *Gambar 5.3 Keuntungan tersimpan di cara kerja: bila program dihentikan 2031, biaya naik lagi. Sumber: model system dynamics tim.*

### 5.5 Key Performance Indicators

Kolom gate 2027 sekaligus menjadi kriteria lanjut program.

| KPI | Jenis | Baseline | Gate 2027 | Target 2030 |
|---|---|---|---|---|
| Indeks biaya konversi (harga konstan 2025) | Hasil | 106 | — | ≤ 101 (potensi 96,9) |
| Laju belajar: perubahan indeks per tahun | Hasil | +3 poin/tahun | Berhenti naik | ≤ −3 poin/tahun |
| Penurunan scrap di area pilot | Hasil | 0% | ≥ 60% | — |
| Indeks scrap pabrik | Hasil | 108 | — | 78 |
| Indeks cacat lolos ke hilir | Hasil | 103 | — | 73 |
| Indeks unplanned downtime | Hasil | 111 | — | 90 |
| Bulan per perubahan varian | Hasil | 9 | — | 7,2 |
| CO₂ dihindari | Keberlanjutan | 0 | — | 1.765 t/tahun |
| Operator yang mengabaikan alert | Pendorong | 31% | ≤ 20% | 10% |
| Waktu engineer untuk perbaikan | Pendorong | 25% | ≥ 30% | 41% |
| Ide terimplementasi per engineer per tahun | Pendorong | 0,67 | ≥ 0,75 | ≥ 2,4 |
| Know-how kritis terdokumentasi | Pendorong | 33% | 39% | 64% |
| Engineer software & AI L3+ | Pendorong | 2 | 4,9 | 13,6 |
| Operator terlatih alat berbasis data | Pendorong | 18% | 50% | 90% |

---

## BAB 6. KESIMPULAN DAN REKOMENDASI

**Paragraf rangkuman:**
Keunggulan TMMIN berikutnya bukan peralatan yang lebih canggih, melainkan pabrik yang kembali belajar. Hari ini selisih biaya melebar 5,5 poin per tahun dan semua indikator internal memburuk, karena sinyal dan pelajaran tidak punya jalur kembali.

Closed-Loop Kaizen menjawab keempat sub-pertanyaan sebagai satu sistem:
- menutup celah terbesar di antara proses;
- mengubah cara kerja dengan manusia di pusatnya dan waktu perbaikan yang dilindungi;
- dibangun bertahap dengan gate dan akademi;
- menghasilkan nilai yang terukur dan tahan uji: indeks biaya 97–101 pada 2030 dibanding sekitar 114 tanpa tindakan, NPV Rp27–31 miliar, sekitar 1.765 ton CO₂ per tahun dihindari, dan ketergantungan pada senior yang turun hampir separuh.

**Rekomendasi (isi poin-poin di template):**

- **Setujui Fase Persiapan senilai Rp8 miliar** untuk pilot sealer-ke-inspeksi, dimulai setelah validasi kamera AI pada Oktober 2026.
- **Tunjuk satu pemilik standar antarmuka dan data pabrik**, karena standar inilah yang memangkas biaya setiap varian baru.
- **Lindungi 30% waktu perbaikan** bagi team leader dan engineer, dan kunci setiap jam yang dibebaskan loop untuk perbaikan berikutnya.
- **Berkomitmen pada gate akhir 2027:** skalakan program hanya bila keenam kriteria pilot terpenuhi, dan anggarkan pemeliharaan setelah 2030 agar hasilnya bertahan.

---

## DAFTAR PUSTAKA

1. AKTI & TMMIN. (2026). *M3C 2026 Casebook: Next-Level Kaizen*. Exhibit 1–9 (Exhibit 3–9 adalah data dummy).
2. Google Cloud. (2024). *Toyota shifts into overdrive: Developing an AI platform for enhanced manufacturing efficiency*. https://cloud.google.com/blog/topics/hybrid-cloud/toyota-ai-platform-manufacturing-efficiency
3. Microsoft. (2024). *Toyota is deploying AI agents to harness the collective wisdom of engineers and innovate faster*. https://news.microsoft.com/source/asia/features/toyota-is-deploying-ai-agents-to-harness-the-collective-wisdom-of-engineers-and-innovate-faster/
4. Toyota Motor Corporation. (2023). *Electrified technologies: Production process*. https://global.toyota/en/newsroom/corporate/39330500.html
5. Toyota Motor Corporation. (2023). *Monozukuri technology to support the future*. https://global.toyota/en/newsroom/corporate/39758451.html
6. IIoT World. (n.d.). *Predictive maintenance cost savings: Case studies*. https://www.iiot-world.com/predictive-analytics/predictive-maintenance/predictive-maintenance-cost-savings/
7. Siemens. (n.d.). *Using virtual commissioning to reduce commissioning time by 70 percent (Wipro PARI)*. https://resources.sw.siemens.com/en-US/case-study-wipro-pari/
8. Kalypso. (n.d.). *Reducing commissioning time by 40% with a digital twin*. https://kalypso.com/viewpoints/entry/reducing-commissioning-time-by-40-with-a-digital-twin
9. Clean Energy Ministerial. (2022). *Global energy management system implementation: Nissan USA*. https://www.cleanenergyministerial.org/content/uploads/2022/03/cem-em-casestudy-nissan-usa.pdf
10. Repenning, N. P., & Sterman, J. D. (2001). Nobody ever gets credit for fixing problems that never happened. *California Management Review*, 43(4), 64–88.
11. Sterman, J. D. (2000). *Business Dynamics: Systems Thinking and Modeling for a Complex World*. McGraw-Hill.
12. Kementerian ESDM. (2021). *Keputusan Menteri ESDM No. 163.K/HK.02/MEM.S/2021 tentang Penetapan Faktor Emisi Gas Rumah Kaca Sistem Ketenagalistrikan*.
13. CNBC Indonesia. (2025, 3 September). *Tarif listrik PLN per kWh untuk 13 golongan*. https://www.cnbcindonesia.com/news/20250903072445-4-663783/tarif-listrik-pln-per-kwh-untuk-13-golongan-berlaku-3-september-2025
14. Republik Indonesia. (2021). *Undang-Undang No. 7 Tahun 2021 tentang Harmonisasi Peraturan Perpajakan* (pajak karbon).
15. Ohno, T. (1988). *Toyota Production System: Beyond Large-Scale Production*. Productivity Press.

---

## LAMPIRAN

### Lampiran A. Asumsi Utama dan Bukti Pendukung

| Tuas (skenario dasar) | Asumsi model finansial | Hasil system dynamics 2030 vs 2025 | Bukti eksternal |
|---|---|---|---|
| Scrap | −35% | −27% | Simulasi tim: closed loop memangkas scrap di area pilot sekitar 85%; dengan 40% scrap pabrik terjangkau loop, sekitar 34% secara keseluruhan |
| Perawatan / downtime | Biaya −10% | Downtime −19% | McKinsey: predictive maintenance memangkas biaya perawatan 18–25% dan downtime hingga 50% [6] |
| Modifikasi varian | Biaya −35% | Bulan −20% | Virtual commissioning memangkas commissioning di lokasi 70% pada lini mesin 17 varian [7]; hingga 40% [8] |
| Energi | −5% | −5% pada cakupan penuh | Pabrik Nissan di AS meningkatkan kinerja energi 13,8% dalam 3 tahun [9] |
| Waktu NVA operator | −30% | −24% | Platform AI in-house Toyota menghemat lebih dari 10.000 jam per tahun [2]; dikonfirmasi lewat time study di pilot |
| Komposisi biaya konversi | Asumsi tim: tenaga kerja 40%, depresiasi 25%, perawatan 13%, energi 12%, scrap 10% | Sama | Casebook hanya menyebut komponennya; porsi tenaga kerja diuji 35–45% |
| Waktu operator yang menjadi kas | 50% | 50% (diuji 30–70%) | Sisanya dialihkan ke kaizen (tanpa PHK) |

### Lampiran B. Metodologi

- **Model finansial:**
  - Model lima tahun (2026–2030) dengan parameter Exhibit 9: diskonto 10%, umur teknologi 5 tahun, eskalasi biaya 4% per tahun, 175.000 unit, dan biaya konversi Rp3,2 juta per unit.
  - Penghematan naik bertahap 10%, 35%, 65%, 90%, dan 100% dari kapasitas penuh.
  - Belanja modal 10%, 15%, 40%, 25%, dan 10%.
  - Biaya operasional 10% dari investasi kumulatif, ditambah Rp2,5 miliar per tahun untuk pelatihan dan manajemen perubahan.
- **Simulasi sealer:** Monte Carlo berbasis episode drift sealer. Membandingkan inspeksi manual di akhir lini, kamera yang lebih baik di akhir lini, dan closed loop tepat setelah sealer; 300 simulasi per skenario, dengan uji sensitivitas pada lima parameter proses dan tingkat pengabaian alert.
- **Model system dynamics:**
  - *Struktur:* model stock-and-flow, langkah bulanan, 2023–2035. Stok: kolam masalah, kapabilitas perbaikan (jebakan firefighting [10]), know-how terdokumentasi, engineer software & AI per level, kepatuhan alert, serta cakupan loop dan standar data.
  - *Kalibrasi:* tiga parameter dikalibrasi agar skenario tanpa tindakan mereproduksi Exhibit 4 dan 6A pada 2025 (galat < 3%).
  - *Penahan:* loop penyeimbang (perbaikan gejala oleh firefighting, lantai masalah yang tidak bisa dihilangkan, batas produktivitas 2×) menjaga hasil di bawah benchmark eksternal.
  - *Ekonomi:* NPV dibandingkan dengan skenario tanpa tindakan dan dengan kinerja yang dibekukan di 2025.
  - *Keberlanjutan:* energi, CO₂, scrap, keterampilan, ketergantungan pada senior, dan ketahanan sampai 2035.
  - *Uji stres:* Monte Carlo 1.500 simulasi per strategi dengan 18 input segitiga, termasuk uji kegagalan loop.
- **Uji stres model finansial:** 10.000 simulasi dengan 13 input berdistribusi segitiga, lima strategi pendanaan, dan skenario keterlambatan satu tahun.
- **Model kapabilitas:** kenaikan level engineer antar level Exhibit 7 dengan laju akademi yang sama di kedua model.
