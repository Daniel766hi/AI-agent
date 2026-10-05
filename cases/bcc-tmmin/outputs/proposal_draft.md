# Isi Proposal: Closed-Loop Kaizen

> Panduan pakai: salin setiap bagian ke subbab yang sama di `Template_Proposal_M3C2026.docx`. Bagian bertanda **[GAMBAR]** ditempel di kotak "[Sisipkan grafik, diagram, atau gambar di sini]" memakai file PNG yang dilampirkan. Ganti `[Nama Tim]` dan nama anggota di sampul dan footer.

---

## SAMPUL

- **Judul Solusi Tim:** Closed-Loop Kaizen
- **Subjudul:** Pabrik yang belajar dari dirinya sendiri, dengan orang-orang TMMIN sebagai pusatnya
- **Tim:** [Nama Tim] · [Nama Anggota 1] · [Nama Anggota 2] · [Nama Anggota 3] · [Nama Universitas]
- **Footer:** Closed-Loop Kaizen · Tim [Nama Tim] · M3C 2026

---

## RINGKASAN EKSEKUTIF

**Kalimat kunci (kotak garis oranye):**
TMMIN sebaiknya mengubah cara pabriknya belajar, bukan menambah peralatan: dengan menutup tiga loop yang selama ini terbuka, indeks biaya konversi dapat turun dari 106 menjadi sekitar 97 pada 2030, atau menutup kira-kira separuh selisih dengan pemain baru (89).

**Paragraf 1:**
Pasar mobil nasional turun 7,2% pada 2025, sementara biaya konversi per unit TMMIN di Karawang naik ke indeks 106 dan pemain baru turun ke 89, sehingga TMMIN kini sekitar 19% lebih mahal per unit. Di saat yang sama, porsi kendaraan elektrifikasi akan naik dari 30% menjadi 55–70% pada 2030, sehingga lini harus menampung lebih banyak varian. Saat ini sealer yang terlewat baru ditemukan di inspeksi akhir, setelah pengecatan dan perakitan menambah nilai pada unit yang cacat. Sinyalnya ada, tetapi tidak pernah kembali ke sumber masalah.

**Paragraf 2:**
Gagasan kami, **Closed-Loop Kaizen**, menutup tiga loop dengan manusia sebagai pusatnya: (1) loop kualitas berbasis jidoka, agar setiap abnormalitas kembali ke proses penyebabnya dalam hitungan menit; (2) loop data dan peralatan berbasis standardized work, berupa satu standar antarmuka milik TMMIN sehingga varian baru cukup dikonfigurasi, bukan dikabel ulang; (3) loop manusia dan pengetahuan berbasis kaizen dan yokoten, berupa alat AI buatan operator, kanal ide satu ketukan, dan know-how senior yang terdokumentasi. Berbeda dari membeli teknologi, gagasan ini mengubah cara kerja, dan simulasi kami menunjukkan kamera saja justru menaikkan scrap 12%, sedangkan loop tertutup memangkasnya 85%.

**Tabel indikator utama:**

| Indikator utama | Saat ini | Target 2030 |
|---|---|---|
| Indeks biaya konversi (2023 = 100) | 106 | 96,9 |
| Bulan modifikasi peralatan untuk varian baru | 9 | 5,9 |
| Engineer software & AI di level mahir (dari 30) | 2 | sekitar 14 |
| Investasi dan NPV (10%) | Rp80 miliar | NPV Rp27 miliar, payback 2029 |

**Paragraf 3:**
Investasi dibelanjakan secara bertahap (*pilot-light*): hanya 25% sebelum gate go/no-go di akhir 2027. Dari 10.000 simulasi, rencana ini menghasilkan NPV positif pada 85% skenario. Kami meminta TMMIN memutuskan empat hal kuartal ini: menyetujui Rp8 miliar untuk pilot sealer-ke-inspeksi, menunjuk satu pemilik standar data pabrik, melindungi waktu kaizen bagi team leader dan engineer, serta berkomitmen menskalakan program hanya berdasarkan bukti di gate 2027.

---

## BAB 1. PENDAHULUAN

### 1.1 Latar Belakang

Industri otomotif global sedang berubah oleh empat tren teknologi: Connected, Autonomous, Shared, dan Electric (C.A.S.E.). Di Indonesia, perubahan ini terjadi bersamaan dengan pasar domestik yang melemah serta masuknya pemain baru dengan harga agresif dan siklus peluncuran yang cepat.

PT Toyota Motor Manufacturing Indonesia (TMMIN) mengoperasikan lima fasilitas di Jakarta dan Karawang yang memproduksi kendaraan, mesin, dan komponen. Perusahaan sedang bergeser dari fokus *green manufacturing* menuju perusahaan mobilitas, sambil menyiapkan pendekatan multi-pathway yang menampung kendaraan konvensional, HEV, PHEV, dan BEV sekaligus. Periode 2026–2030 adalah jendela terbentuknya posisi kompetitif jangka panjang, sehingga solusi yang dibutuhkan bersifat transformatif, bukan perbaikan jangka pendek.

Sesuai tema besar M3C 2026, *Human-Centered AI Kaizen*, solusi tersebut harus menempatkan manusia di pusatnya. Arah ini sudah dirintis di Toyota Jepang: staf pabrik membangun sekitar 10.000 model AI di platform in-house, dan sistem O-Beya menyimpan pengetahuan engineer senior agar tidak hilang saat mereka pensiun. Paper ini mengadaptasi pelajaran tersebut untuk kondisi TMMIN.

### 1.2 Pertanyaan Kunci

*(Sudah tertulis di template, tidak perlu diubah.)*

### 1.3 Struktur Paper

| Bab | Sub-pertanyaan | Ringkasan jawaban |
|---|---|---|
| 2 | Visi manufaktur masa depan | Pabrik yang belajar lebih cepat daripada yang bisa ditiru pesaing; celah terbesar ada di antara proses, dimulai dari sealer ke inspeksi |
| 3 | Ide transformatif | Closed-Loop Kaizen: tiga loop tertutup dengan manusia di pusatnya, terbukti lewat simulasi |
| 4 | Roadmap dan pengembangan kapabilitas | Lima fase dengan gate di akhir 2027, rencana 100 hari pertama, dan akademi engineer |
| 5 | Dampak kompetitif dan finansial | NPV Rp27 miliar, peluang positif 85%, serta KPI hasil dan pendorong |

Seluruh angka dapat ditelusuri ke Exhibit casebook atau asumsi yang dinyatakan di Lampiran. Exhibit 3–9 adalah data dummy dari panitia.

---

## BAB 2. VISI MANUFAKTUR MASA DEPAN

**Kalimat kunci bab:**
Celah terbesar TMMIN tidak berada di dalam satu proses, melainkan di antara proses: loop kualitas, data, dan pengetahuan masih terbuka, dan area dengan biaya terbesar akibat loop terbuka adalah sealer ke inspeksi.

### 2.1 Situasi Saat Ini

Penjualan wholesales nasional turun 7,2% pada 2025 menjadi 803.687 unit, dan penjualan ritel turun 6,3% menjadi 833.692 unit. Dalam dua tahun, indeks biaya konversi Karawang naik dari 100 ke 106, sementara benchmark pemain baru turun dari 94 ke 89. Artinya TMMIN kini memproduksi sekitar 19% lebih mahal per unit, dan selisihnya melebar setiap tahun.

**[GAMBAR] `fig_cost.png`**
Keterangan: *Gambar 2.1 Selisih biaya konversi melebar setiap tahun. Sumber: Exhibit 3.*

Pada saat yang sama, porsi kendaraan elektrifikasi (HEV, PHEV, BEV) akan naik dari 30% volume pada 2026 menjadi 55% (skenario moderat) atau 70% (skenario agresif) pada 2030. Lini yang sama harus menampung lebih banyak varian tanpa menambah biaya berlebihan.

### 2.2 Komplikasi

| Tekanan | Bukti, 2023 ke 2025 |
|---|---|
| Biaya dan kualitas | Indeks scrap 100 ke 108; unplanned downtime 100 ke 111; cacat lolos ke proses hilir 100 ke 103; waktu non-value-added operator 20% ke 22% |
| Fleksibilitas lini | Modifikasi peralatan untuk varian baru 8 ke 9 bulan; peralatan lintas generasi tersambung point-to-point tanpa standar antarmuka |
| Mindset, pengetahuan, dan talenta | Waktu engineer untuk dukungan rutin 62% ke 65%; waktu perbaikan 28% ke 25%; ide per engineer 3,1 ke 2,4 per tahun; hanya 2 dari 30 engineer mahir software dan AI |

Ketiga tekanan ini datang bersamaan, sehingga perbaikan satu per satu tidak akan cukup.

### 2.3 Akar Masalah

Ketiga komplikasi berakar pada satu pola yang sama: sinyal tidak kembali ke orang yang bisa bertindak. Kami menyebutnya tiga loop yang terbuka.

| Loop | Apa yang terbuka saat ini | Akibatnya |
|---|---|---|
| Kualitas | Inspeksi kualitas, satu-satunya proses Level 1, tidak mengirim hasil kembali ke hulu; sealer belum punya umpan balik kualitas otomatis | Cacat ditemukan terlambat dan berujung scrap |
| Data dan peralatan | Integrasi data di Level 1; peralatan lintas generasi tersambung point-to-point | Setiap varian baru butuh sekitar 9 bulan pengerjaan ulang |
| Manusia dan pengetahuan | 48% proses kritis bergantung pada 1–2 senior; hanya 33% know-how terdokumentasi; 71% berbagi pengetahuan lewat coaching informal | Engineer sibuk memadamkan masalah; ide menurun; 31% operator mengabaikan alert |

Survei yang sama juga menunjukkan peluang: 62% operator mau menyumbang ide bila ada kanal yang mudah, dan 54% sudah melihat teknologi sebagai pembantu, bukan pengganti.

### 2.4 Visi 2030 dan Nilai Baru di Luar Biaya

Pada 2030, keunggulan TMMIN adalah kecepatan pabriknya belajar, sesuatu yang tidak bisa dibeli dari luar. Biaya rendah adalah hasil, bukan visinya. Nilai baru di luar biaya ada tiga:

- **Kecepatan:** varian baru siap produksi dalam sekitar 6 bulan, bukan 9.
- **Pengetahuan yang bertumbuh:** lebih dari 80% know-how kritis terdokumentasi; engineer baru mandiri dalam 9 bulan, bukan 15.
- **Orang yang terlibat:** operator dan engineer membangun alat mereka sendiri; ide per engineer naik dari 2,4 menjadi sekitar 4,3 per tahun.

### 2.5 Area Prioritas

| Proses / fungsi | Level saat ini | Celah utama | Dampak ke biaya & kualitas |
|---|---|---|---|
| Inspeksi kualitas | 1 dari 4 | Inspeksi visual manual; hasil tidak kembali ke hulu | Cacat ditemukan terlambat, scrap dan cacat lolos naik |
| Integrasi data | 1 dari 4 | Data peralatan, kualitas, dan logistik belum terhubung | Sinyal tidak bisa dirutekan; varian baru butuh pengerjaan ulang |
| Sealer application | 2 dari 4 | Manual dan semi-otomatis; belum ada umpan balik kualitas otomatis | Bead yang terlewat dapat membuat unit di-scrap |

Kami memulai di area sealer ke inspeksi karena tiga alasan. Pertama, cerita biayanya paling jelas: bead yang terlewat ditemukan di akhir dan dapat membuat unit di-scrap. Kedua, fondasinya sudah tersedia, yaitu kamera AI in-house dari CCTV yang selesai divalidasi pada Oktober 2026. Ketiga, pilot ini menyentuh ketiga loop sekaligus: umpan balik kualitas, koneksi data antar dua proses, dan know-how operator.

---

## BAB 3. IDE TRANSFORMATIF

**Kalimat kunci bab:**
Closed-Loop Kaizen mengubah cara pabrik bekerja, bukan apa yang dibelinya: setiap sinyal, dari kamera, sensor, atau operator, kembali ke orang yang bisa bertindak, dan setiap perbaikan menjadi standar yang lebih baik.

### 3.1 Gambaran Gagasan

Closed-Loop Kaizen terdiri dari tiga loop yang saling menguatkan, masing-masing berakar pada prinsip Toyota Production System:

| Loop | Prinsip TPS | Perubahan cara kerja |
|---|---|---|
| Loop kualitas | Jidoka | Setiap abnormalitas kembali ke proses penyebabnya dalam hitungan menit, dengan aturan jelas: stop, koreksi, atau eskalasi. Operator mengonfirmasi dan memperbaiki di stasiun. |
| Loop data dan peralatan | Standardized work | Satu standar antarmuka dan data milik TMMIN. Peralatan baru tinggal disambungkan; varian baru menjadi konfigurasi, bukan pengkabelan ulang. |
| Loop manusia dan pengetahuan | Kaizen dan yokoten | Alat AI buatan operator, kanal ide satu ketukan, dan know-how senior yang terdokumentasi mengubah keahlian individu menjadi standar bersama. |

Manusia tetap di pusat secara desain: operator mengonfirmasi dan memperbaiki, team leader menyetel aturan alert, engineer melatih dan membangun. Teknologi hanya membawa sinyal.

**[GAMBAR] Diagram sistem (buat sendiri di PowerPoint/Canva):** tiga kotak berdampingan berjudul *Loop kualitas*, *Loop data & peralatan*, *Loop manusia & pengetahuan*, dengan satu lingkaran "Orang TMMIN" di tengah yang terhubung ke ketiganya.
Keterangan: *Gambar 3.1 Tiga loop Closed-Loop Kaizen dengan manusia sebagai pusat.*

### 3.2 Cara Kerja

Satu siklus Closed-Loop Kaizen, dengan contoh bead sealer yang terlewat:

1. **Deteksi:** kamera, sensor, atau operator menemukan bead sealer yang terlewat.
2. **Rutekan:** standar data mengirim sinyal ke stasiun sealer dalam hitungan detik.
3. **Bertindak:** operator menghentikan, mengoreksi, dan mengonfirmasi (jidoka di stasiun).
4. **Belajar:** team leader meninjau penyebab dan setiap alert yang diabaikan di kaizen harian.
5. **Standarkan:** perbaikan masuk standard work dan disebarkan ke lini lain (yokoten).

Saat ini hanya langkah 1 yang sebagian ada. Langkah 2, 4, dan 5 yang hilang, dan itulah alasan kamera saja tidak menyelesaikan masalah.

### 3.3 Bukti dan Validasi

Kami membangun simulasi Monte Carlo untuk drift sealer: 175.000 unit per tahun dan 300 simulasi per skenario. Parameter proses merupakan asumsi ilustratif; temuannya adalah mekanisme, bukan angka absolut.

**[GAMBAR] `fig_sim.png`**
Keterangan: *Gambar 3.2 Menutup loop memangkas scrap 85%; kamera saja justru menaikkannya. Sumber: simulasi tim.*

Kamera yang lebih baik di akhir lini menemukan lebih banyak unit cacat, tetapi terlambat untuk menyelamatkannya, sehingga scrap justru naik 12%. Menutup loop tepat setelah sealer menghentikan drift dalam beberapa unit dan memangkas scrap 85%. Bila operator mengabaikan alert seperti tingkat saat ini (31%), seperlima manfaat hilang: kepercayaan adalah bagian dari nilai. Di seluruh uji sensitivitas, penurunan scrap di area pilot tidak pernah di bawah sekitar 80%.

Gagasan ini juga didukung preseden publik: platform AI in-house Toyota di Jepang dipakai staf pabrik untuk membangun model inspeksi dan deteksi abnormalitas, dan menghemat lebih dari 10.000 jam kerja per tahun.

### 3.4 Manusia sebagai Pusat: Mindset dan Pengetahuan

Pola pikir berubah ketika waktu, kanal, dan pengakuan berubah, bukan hanya lewat pelatihan. Tiga mekanismenya:

| Mekanisme | Baseline | Target 2030 |
|---|---|---|
| Bebaskan waktu: know-how bersama dan alat buatan sendiri menyerap troubleshooting rutin | 65% waktu engineer untuk dukungan rutin | 45%; sekitar 10.800 jam perbaikan tambahan per tahun |
| Mudahkan ide: kanal satu ketukan, respons 48 jam, apresiasi di rapat tim | 62% operator mau berkontribusi | Ide per engineer 2,4 menjadi sekitar 4,3 per tahun |
| Tangkap know-how: sprint dengan senior, wawancara berbantuan AI yang divalidasi ahli, ditautkan ke standard work | 33% terdokumentasi | Sekitar 83% terdokumentasi |

**Tabel peran (isi tabel template):**

| Peran | Saat ini | Dengan gagasan tim |
|---|---|---|
| Operator | Mengecek sealer secara visual; tahu ada miss berjam-jam kemudian | Menerima alert beberapa detik setelah miss, memperbaiki di stasiun, mencatat ide dengan satu ketukan |
| Team leader | Eskalasi dengan berjalan dan telepon; alert yang terlalu sering diabaikan | Mengelola satu papan abnormalitas; menyetel aturan alert bersama tim |
| Engineer | 65% waktu untuk dukungan rutin; engineer baru butuh 15 bulan untuk mandiri | Membangun standar dan alat; 45% waktu untuk perbaikan; engineer baru mandiri dalam sekitar 9 bulan |

### 3.5 In-house dan Kemitraan

Prinsipnya: bangun sendiri yang menjadi pembeda dan yang nilainya bertumbuh bila dimiliki; bermitra hanya untuk komoditas atau teknologi yang benar-benar khusus.

| Komponen | Pilihan | Alasan |
|---|---|---|
| Logika loop dan aturan alert | Bangun | Know-how inti, terikat ke standard work |
| Standar antarmuka dan data pabrik | Bangun | Kepemilikan inilah yang memangkas biaya varian |
| Model inspeksi AI | Bangun | Melanjutkan kamera CCTV in-house |
| Peralatan dan fixture standar | Bangun | Lebih murah, fleksibel, memakai engineer sendiri |
| Komputasi dan cloud | Mitra | Komoditas, bukan pembeda |
| Sensor canggih, teknologi proses baterai | Mitra | Teknologi khusus, dengan klausul transfer pengetahuan |

### 3.6 Alternatif yang Dipertimbangkan

Kami menilai delapan opsi dengan enam kriteria berbobot. Empat opsi yang paling sering diusulkan gagal bila berdiri sendiri:

| Opsi | Mengapa gagal bila berdiri sendiri |
|---|---|
| Kamera AI di seluruh lini | Menemukan cacat terlambat (scrap +12% di simulasi kami); tidak membangun kapabilitas |
| Lini tanpa konveyor dengan AGV/AMR | Padat modal, jawaban berbasis peralatan, sulit masuk rentang Rp40–120 miliar |
| Predictive maintenance saja | Tidak menyentuh loop kualitas dan pengetahuan |
| Program pelatihan saja | Sinyal tetap tidak kembali; baru 18% operator terlatih |

Closed-Loop Kaizen mengambil yang terbaik dari masing-masing opsi: kamera dan data maintenance mengisi loop, otomasi bergerak mengikuti standar data, dan pelatihan terjadi pada pekerjaan pilot nyata.

---

## BAB 4. ROADMAP DAN PENGEMBANGAN KAPABILITAS

**Kalimat kunci bab:**
Kami membelanjakan sedikit sebelum terbukti berhasil: 25% belanja modal dikeluarkan sebelum gate go/no-go di akhir 2027, dan sisanya hanya diskalakan berdasarkan bukti.

### 4.1 Tahapan Implementasi 2026–2030

| Fase | Periode | Kegiatan utama | Porsi investasi | Kriteria lanjut (gate) |
|---|---|---|---|---|
| Persiapan & Pilot | Q4 2026–2027 | Loop sealer di kamera CCTV; draf standar data; kanal ide aktif; closed loop berjalan; alat buatan operator pertama; know-how kritis ditangkap | 25% (10% + 15%) | Gate akhir 2027: adopsi pilot ≥ 80% dan penghematan sesuai rencana |
| Standardisasi | 2028 | Disalin ke 2–3 area; standar data wajib untuk peralatan baru | 40% | Standar terbukti di minimal 2 area |
| Roll-out | 2029 | Seluruh lini kendaraan Karawang; retrofit peralatan lama sesuai prioritas | 25% | Roll-out sesuai anggaran |
| Skala penuh | 2030 | Pabrik mesin; perubahan varian lewat konfigurasi | 10% | Target KPI 2030 tercapai |

Bila gate 2027 tidak terpenuhi, pilot tetap berjalan tetapi belanja modal berikutnya dihentikan. Desain ini terbukti penting di uji stres kami: peluang NPV positif naik dari 49% (belanja di awal, tanpa gate) menjadi 85% (pilot-light dengan gate).

**[GAMBAR] Timeline roadmap (buat sendiri):** lima kotak berurutan Persiapan (Q4 2026, 10%) → Pilot (2027, 15%) → Standardisasi (2028, 40%) → Roll-out (2029, 25%) → Skala (2030, 10%), dengan garis putus-putus dan belah ketupat "Gate akhir 2027" di antara Pilot dan Standardisasi.
Keterangan: *Gambar 4.1 Hanya seperempat belanja modal dikeluarkan sebelum gate 2027.*

**Seratus hari pertama** (dapat ditambahkan sebagai paragraf atau tabel di bawah 4.1). Seratus hari pertama hanya memakai apa yang sudah dimiliki TMMIN: kamera CCTV yang tervalidasi, operator, dan team leader.

| Hari | Fokus | Aksi |
|---|---|---|
| 1–30 | Lihat | Genchi genbutsu di sealer-ke-inspeksi bersama operator; baseline scrap, cacat lolos, dan alert yang diabaikan; tunjuk pemilik standar data; luncurkan kanal ide |
| 31–60 | Hubungkan | Sambungkan kamera tervalidasi ke alert sealer dan andon digital; rancang aturan alert bersama team leader; sprint pertama penangkapan know-how |
| 61–100 | Jalankan | Loop berjalan di satu shift, lalu semua shift; kaizen mingguan untuk setiap alert yang diabaikan; kohort akademi pertama membangun alat pertamanya |

Kecepatan pilot sangat menentukan: bila penghematan terlambat satu tahun, peluang NPV positif turun dari 85% menjadi 33%.

### 4.2 Pengembangan Talenta dan Pengetahuan

Engineer software dan AI yang mahir (level 3 ke atas) akan naik dari 2 menjadi sekitar 14 dari 30 pada 2030, dibangun di atas kekuatan TMMIN yang sudah ada di bidang mekanikal dan elektrikal.

**[GAMBAR] `fig_capability.png`**
Keterangan: *Gambar 4.2 Jumlah engineer di level 3 ke atas. Sumber: Exhibit 7 dan model kapabilitas tim.*

- **Kohort berjenjang:** 30% engineer Level 1 dan 20% engineer Level 2 naik level setiap tahun (asumsi tim, diuji di pilot).
- **Belajar di pilot:** setiap kohort membangun satu alat nyata untuk lini.
- **Mengajar kembali:** engineer Level 3 menjadi pelatih mulai 2029.
- **Operator juga:** pelatihan alat berbasis data naik dari 18% menjadi 90% operator.
- **Penangkapan pengetahuan:** know-how kritis dari senior didokumentasikan lewat sprint terjadwal, divalidasi ahli, dan ditautkan ke standard work, sehingga engineer baru mandiri dalam 9 bulan, bukan 15.

### 4.3 Kolaborasi dengan Mitra

Mitra hanya dilibatkan ketika menambah nilai yang khas, seperti sensor canggih dan teknologi proses baterai, dan setiap kontrak memuat klausul transfer pengetahuan. Logika loop, standar data, dan model AI tetap in-house. Program dipimpin satu pemilik program, dengan pemilik standar data dan forum kaizen mingguan di area pilot.

### 4.4 Risiko dan Mitigasi

| Risiko | Peluang (1–5) | Dampak (1–5) | Mitigasi | Indikator peringatan |
|---|---|---|---|---|
| Operator tidak percaya atau mengabaikan alert | 4 | 5 | Rancang alert bersama team leader; alert yang menjelaskan alasan; pelatihan sebelum go-live; setiap pengabaian ditinjau di kaizen | Tingkat pengabaian alert (31% saat ini) |
| Integrasi peralatan lama sulit | 4 | 4 | Mulai dari area pilot; standar wajib untuk peralatan baru; retrofit bertahap sesuai prioritas | Porsi peralatan pilot pada standar |
| Keterampilan software dan AI kurang | 4 | 4 | Kohort akademi; bermitra untuk pembangunan pertama dengan transfer pengetahuan | Jumlah engineer level 3+ |
| Adopsi pilot di bawah rencana | 3 | 5 | Pendanaan pilot-light; gate go/no-go akhir 2027 | Adopsi dan penghematan pilot terhadap rencana |
| Penghematan datang terlambat | 3 | 5 | Mulai dari kamera CCTV yang ada; rencana 100 hari; tinjauan KPI mingguan | Penghematan pilot per kuartal |
| Senior tidak punya waktu berbagi know-how | 3 | 3 | Sprint penangkapan yang dilindungi; pengakuan; wawancara berbantuan AI | Porsi know-how terdokumentasi |
| Kamera AI gagal validasi Oktober 2026 | 2 | 4 | Loop tidak bergantung pada satu sensor: andon digital dan cek operator selama model dilatih ulang | Akurasi validasi terhadap ambang |

---

## BAB 5. DAMPAK KOMPETITIF DAN FINANSIAL

**Kalimat kunci bab:**
Program Rp80 miliar menghasilkan NPV Rp27 miliar pada tingkat diskonto 10% dan balik modal pada 2029; program sudah impas bila hanya menutup 22% selisih biaya dengan pemain baru.

### 5.1 Dampak pada Biaya, Kualitas, Waktu, Fleksibilitas, dan Kapabilitas

| Dimensi | Indikator | Saat ini | 2030 |
|---|---|---|---|
| Biaya | Indeks biaya konversi (2023 = 100) | 106 | 96,9 |
| Kualitas | Indeks scrap | 108 | 75 |
| Waktu | Bulan modifikasi peralatan untuk varian baru | 9 | 5,9 |
| Fleksibilitas | Proses pada standar data bersama | 0% | 80% |
| Kapabilitas SDM | Engineer software & AI level 3+ (dari 30) | 2 | sekitar 14 |

### 5.2 Kebutuhan Investasi dan Analisis Finansial

Pada kapasitas penuh, program menghemat Rp48 miliar per tahun, atau 8,6% dari biaya konversi Karawang sebesar Rp560 miliar (175.000 unit × Rp3,2 juta). Pada 2030, penghematan bruto per tuas dalam skenario dasar adalah scrap Rp22,9 miliar, modifikasi varian Rp12,3 miliar, waktu operator Rp8,6 miliar, perawatan Rp8,5 miliar, dan energi Rp3,9 miliar.

| Rp miliar | Konservatif | Dasar | Optimis |
|---|---|---|---|
| Investasi | 110 | 80 | 60 |
| Penghematan per tahun (kapasitas penuh) | 25,9 | 48,1 | 70,4 |
| NPV (10%, 2026–2030) | (55,4) | 27,0 | 102,4 |
| Payback | Setelah 2030 | 2029 | 2027 |

**[GAMBAR] `fig_savings.png`**
Keterangan: *Gambar 5.1 Penghematan bruto per tuas, skenario dasar. Sumber: model finansial tim berdasarkan Exhibit 9.*

Jika umur peralatan setelah 2030 dihitung pada nilai buku, NPV dasar naik menjadi Rp53 miliar. Skenario konservatif bernilai negatif, dan itulah alasan roadmap memakai gate. Kami tidak menonjolkan IRR karena dengan belanja hanya 10% di 2026, IRR tampak terlalu tinggi.

**Uji stres.** Kami mengubah 13 input yang tidak pasti secara bersamaan dalam 10.000 simulasi, mulai dari besar tiap tuas penghematan hingga investasi, adopsi, dan realisasi kas.

**[GAMBAR] `fig_stress.png`**
Keterangan: *Gambar 5.2 Peluang NPV positif per strategi pendanaan. Sumber: simulasi Monte Carlo tim.*

Input yang paling menggerakkan NPV adalah besar investasi, tingkat adopsi, dan penurunan scrap. Kecepatan pilot adalah faktor penentu, sehingga rencana 100 hari pertama diletakkan paling depan.

### 5.3 Key Performance Indicators

Kolom target pilot sekaligus menjadi kriteria gate 2027.

| KPI | Jenis | Baseline | Target pilot (2027) | Target 2030 |
|---|---|---|---|---|
| Indeks biaya konversi | Hasil | 106 | 102 | 97 |
| Indeks scrap | Hasil | 108 | 95 | 75 |
| Indeks cacat lolos ke hilir | Hasil | 103 | 90 | 60 |
| Indeks unplanned downtime | Hasil | 111 | 100 | 75 |
| Bulan per perubahan varian | Hasil | 9 | 7 | 5,9 |
| Operator yang mengabaikan alert | Pendorong | 31% | 20% | 10% |
| Operator terlatih alat berbasis data | Pendorong | 18% | 50% | 90% |
| Waktu engineer untuk perbaikan | Pendorong | 25% | 30% | 45% |
| Ide per engineer per tahun | Pendorong | 2,4 | 3,0 | 4,3 |
| Know-how kritis terdokumentasi | Pendorong | 33% | 50% | 83% |
| Engineer software & AI level 3+ | Pendorong | 2 | 6 | 14 |

---

## BAB 6. KESIMPULAN DAN REKOMENDASI

**Paragraf rangkuman:**
Keunggulan TMMIN berikutnya bukan peralatan yang lebih canggih, melainkan pabrik yang belajar dari dirinya sendiri: sinyal kembali ke orang yang bisa bertindak, dan setiap perbaikan menjadi standar. Closed-Loop Kaizen menjawab keempat sub-pertanyaan sebagai satu sistem. Ia menutup celah terbesar di antara proses, mengubah cara kerja dengan manusia di pusatnya, dibangun bertahap dengan gate dan akademi, serta menghasilkan nilai yang terukur dan tahan uji: indeks biaya 106 menjadi sekitar 97, varian baru siap dalam 6 bulan, dan NPV Rp27 miliar.

**Rekomendasi (isi poin-poin di template):**

- **Setujui Fase Persiapan senilai Rp8 miliar** untuk pilot sealer-ke-inspeksi, dimulai setelah validasi kamera AI pada Oktober 2026.
- **Tunjuk satu pemilik standar antarmuka dan data pabrik**, karena standar inilah yang memangkas biaya setiap varian baru.
- **Lindungi waktu kaizen** bagi team leader, engineer, dan senior, sebagai syarat agar know-how berpindah dari individu ke sistem.
- **Berkomitmen pada gate akhir 2027:** skalakan program hanya bila adopsi pilot minimal 80% dan penghematan sesuai rencana.

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

---

## LAMPIRAN

### Lampiran A. Asumsi Utama dan Bukti Pendukung

| Tuas (skenario dasar) | Bukti |
|---|---|
| Scrap −35% | Simulasi tim: closed loop memangkas scrap di area pilot sekitar 85%; dengan 40% scrap pabrik berada di area tersebut, sekitar 34% secara keseluruhan |
| Biaya perawatan −10% | McKinsey melaporkan predictive maintenance memangkas biaya perawatan 18–25% [6]; rentang kami lebih rendah |
| Biaya modifikasi varian −35% | Virtual commissioning memangkas commissioning di lokasi 70% pada lini mesin 17 varian [7]; hingga 40% [8] |
| Energi −5% | Pabrik Nissan di AS meningkatkan kinerja energi 13,8% dalam 3 tahun [9] |
| Waktu non-value-added operator −30% | Platform AI in-house Toyota menghemat lebih dari 10.000 jam per tahun [2]; dikonfirmasi lewat time study di pilot |
| Komposisi biaya konversi | Asumsi tim: tenaga kerja 40%, depresiasi 25%, perawatan 13%, energi 12%, scrap 10%; porsi tenaga kerja diuji 35–45% |
| Waktu operator yang menjadi kas | 50%; sisanya dialihkan ke kaizen (tanpa PHK) |

### Lampiran B. Metodologi

- **Model finansial:** model lima tahun (2026–2030) dengan parameter Exhibit 9: diskonto 10%, umur teknologi 5 tahun, eskalasi biaya 4% per tahun, 175.000 unit, dan biaya konversi Rp3,2 juta per unit. Penghematan naik bertahap 10%, 35%, 65%, 90%, dan 100% dari kapasitas penuh; belanja modal 10%, 15%, 40%, 25%, dan 10%. Biaya operasional 10% dari investasi kumulatif ditambah Rp2,5 miliar per tahun untuk pelatihan dan manajemen perubahan.
- **Simulasi kualitas:** Monte Carlo berbasis episode drift sealer, membandingkan inspeksi manual di akhir lini dengan closed loop tepat setelah sealer; 300 simulasi per skenario dan uji sensitivitas pada lima parameter proses.
- **Uji stres:** 10.000 simulasi dengan 13 input berdistribusi segitiga, lima strategi pendanaan, dan skenario keterlambatan satu tahun.
- **Model kapabilitas:** kenaikan level engineer antar level Exhibit 7 serta penurunan waktu dukungan rutin 4 poin persentase per tahun.
