# Stage 3 — Opsi Solusi

> Input: `work/2_diagnosis.md`. Setiap opsi harus menutup minimal satu driver di issue tree (kode A1–D4) dan punya preseden publik atau alasan mengapa ia baru. Opsi yang hanya membeli alat ditandai **[BELI]**; opsi yang mengubah sistem kerja ditandai **[SISTEM]**.

## 0. Apa yang harus dipenuhi sebuah opsi (dari Stage 2)

1. Menaikkan **laju perbaikan tahunan**, bukan sekadar memperbaiki kinerja satu kali. Kembali ke kinerja 2023 hanya menutup 11–19% selisih.
2. Membuat **jalur balik**: ke proses penyebab, ke standar bersama, atau ke varian berikutnya.
3. Mengubah **cara manufaktur** (casebook: bukan produk atau alat), dengan manusia di pusat.
4. Masuk dalam Rp40–120 miliar dan periode 2026–2030.

## 1. Dua belas opsi lintas tuas

| # | Opsi | Tuas | Jenis | Mekanisme inti | Driver yang ditutup |
|---|---|---|---|---|---|
| A | Closed-Loop Jidoka | Proses | SISTEM | Abnormalitas dari inspeksi dirutekan ke proses penyebab dalam hitungan menit, dengan aturan stop, koreksi, atau eskalasi | A3, B |
| B | Plug-and-Produce Standard | Data & peralatan | SISTEM | Satu standar antarmuka dan data milik TMMIN; peralatan baru tinggal disambung, varian baru menjadi konfigurasi | C, A4 |
| C | Citizen AI Tools | Manusia | SISTEM | Operator dan engineer membangun alat AI sendiri tanpa coding, di atas platform internal | D2, D4 |
| D | Shop-Floor O-Beya | Pengetahuan | SISTEM | Know-how senior ditangkap lewat sprint dan wawancara berbantuan AI, divalidasi ahli, ditautkan ke standard work | D3 |
| E | Simulation-First Variant Prep | Proses & data | SISTEM | Varian baru diuji di model digital (virtual commissioning) sebelum peralatan diubah fisik | C |
| F | Lini tanpa konveyor + AMR | Peralatan | BELI | Tata letak modular dengan mobile robot; lini disusun ulang per varian | A1, C |
| G | Autonomous & Predictive Maintenance | Peralatan & manusia | Campuran | Operator merawat mesin harian (TPM); data mesin memprediksi kerusakan | A2 |
| H | Firefighting Firewall | Organisasi | SISTEM | Kapasitas perbaikan dilindungi: porsi waktu engineer dikunci untuk akar masalah, dan masalah yang berulang 3 kali wajib masuk antrean akar masalah | D1, D2 |
| I | Operator Idea Engine | Manusia & organisasi | SISTEM | Kanal ide satu ketukan, respons 48 jam, pengakuan di rapat tim, ide kecil langsung dieksekusi team leader | D2 |
| J | Learning-Rate Governance | Organisasi | SISTEM | Pabrik dikelola dengan target "poin indeks biaya turun per tahun" (genka kaizen), bukan target level statis | D, A |
| K | Digital Skill Academy | Manusia | SISTEM | Kohort berjenjang; setiap kohort membangun satu alat nyata di lini; Level 3 mengajar kembali | D4 |
| L | Energy Data Loop | Data & keberlanjutan | SISTEM | Data energi per mesin dan per shift dikembalikan ke team leader; kontrol idle dan standby menjadi bagian standard work | A4 |

## 2. Detail per opsi

### A. Closed-Loop Jidoka [SISTEM]
- **Prinsip:** jidoka dan andon (Ohno, 1988); deteksi dekat sumber lebih murah daripada deteksi di akhir.
- **Preseden:** Toyota AI Platform, tempat staf pabrik Toyota membangun model inspeksi dan deteksi abnormalitas sendiri (sekitar 10.000 model; >10.000 jam kerja per tahun dihemat) [Google Cloud, 2024].
- **Bukti tim:** simulasi drift sealer menunjukkan loop tertutup menurunkan indeks scrap area pilot ke 15–34, sedangkan kamera saja ke 112 (`data/research.md`, Tes 1).
- **Kekuatan:** dampak biaya dan kualitas paling langsung; fondasi kamera AI in-house sudah ada.
- **Kelemahan:** butuh integrasi data dulu (opsi B); gagal jika operator tidak percaya alert (31% mengabaikan).

### B. Plug-and-Produce Standard [SISTEM]
- **Prinsip:** standardized work diterapkan pada mesin dan data; standar terbuka seperti OPC UA (IEC 62541) membuat peralatan dari pemasok berbeda bisa saling bicara.
- **Preseden:** pabrik BEV generasi berikut Toyota menargetkan lead time persiapan dan investasi pabrik turun 50% lewat verifikasi proses digital [Toyota, 2023].
- **Kekuatan:** satu-satunya opsi yang menyerang 9 bulan per varian di akarnya (point-to-point); nilainya bertambah setiap varian baru.
- **Kelemahan:** cerita "manusia"-nya lemah bila berdiri sendiri; peralatan lama perlu retrofit bertahap.

### C. Citizen AI Tools [SISTEM]
- **Prinsip:** Human-Centered AI (Shneiderman, 2022) dan Industry 5.0 (European Commission, 2021): AI memperkuat orang, bukan menggantikannya.
- **Preseden:** Toyota AI Platform, sekitar 1.200 pengguna aktif dan 400+ peserta pelatihan per tahun [Google Cloud, 2024].
- **Kekuatan:** paling human-centered; menaikkan hasil per jam perbaikan, yang menurut Stage 2 turun 31%.
- **Kelemahan:** butuh tata kelola model dan pelatihan; risiko "alat liar" tanpa standar.

### D. Shop-Floor O-Beya [SISTEM]
- **Prinsip:** yokoten; know-how tacit menjadi standar eksplisit.
- **Preseden:** O-Beya Toyota, sistem AI generatif dengan 9 agen spesialis untuk menyimpan pengetahuan sekitar 800 engineer powertrain [Microsoft, 2024].
- **Kekuatan:** murah dan cepat; memanfaatkan coaching informal yang sudah ada (71%); menyerang ketergantungan pada 1–2 senior (48%).
- **Kelemahan:** dampak biaya langsung kecil; butuh waktu senior.

### E. Simulation-First Variant Prep [SISTEM]
- **Prinsip:** front-loading; masalah diselesaikan di model sebelum di lantai produksi.
- **Preseden:** virtual commissioning memangkas commissioning di lokasi 70% pada lini mesin 17 varian [Siemens, Wipro PARI]; hingga 40% [Kalypso].
- **Kekuatan:** kuat untuk kecepatan varian di era multi-pathway.
- **Kelemahan:** butuh data peralatan yang andal dan standar antarmuka (B) lebih dulu; kapabilitas simulasi internal belum ada.

### F. Lini tanpa konveyor + AMR [BELI]
- **Prinsip:** fleksibilitas tata letak.
- **Preseden:** self-propelled assembly line di pabrik BEV Toyota [Toyota, 2023]; AMR menghilangkan hingga 15 km jalan kaki per pekerja per hari [Omron].
- **Kekuatan:** fleksibilitas fisik besar.
- **Kelemahan:** padat modal, terbaca sebagai rekomendasi alat, sulit masuk Rp40–120 miliar untuk dua lini, dan tidak membangun laju belajar.

### G. Autonomous & Predictive Maintenance [Campuran]
- **Prinsip:** Total Productive Maintenance (Nakajima, 1988).
- **Preseden:** predictive maintenance memangkas biaya perawatan 18–25% dan downtime hingga 50% [McKinsey, via IIoT World].
- **Kekuatan:** menyerang driver dengan penurunan terbesar (downtime +11%).
- **Kelemahan:** cakupan sempit; banyak tim lain akan mengusulkannya; tidak menyentuh loop kualitas dan pengetahuan.

### H. Firefighting Firewall [SISTEM] — opsi baru dari Stage 2
- **Prinsip:** *capability trap* (Repenning & Sterman, 2001). Saat masalah menumpuk, orang memadamkan api dan memotong waktu perbaikan, sehingga masalah makin banyak. Satu-satunya jalan keluar adalah melindungi waktu perbaikan sementara kinerja jangka pendek turun sedikit.
- **Preseden:** studi Repenning & Sterman di beberapa pabrik otomotif dan elektronik AS; aturan "masalah berulang menjadi proyek akar masalah" juga dipakai dalam praktik A3 problem solving Toyota.
- **Mengapa baru untuk kasus ini:** data Ex.6A menunjukkan pola capability trap secara tepat: waktu rutin naik (62% → 65%), waktu perbaikan turun (28% → 25%), dan masalah bertambah.
- **Kekuatan:** murah (hampir tanpa capex); menjadi "pemantik" agar loop lain bisa berputar.
- **Kelemahan:** ada masa turun sementara; butuh komitmen manajemen untuk tidak menarik waktu yang dilindungi saat krisis.

### I. Operator Idea Engine [SISTEM]
- **Prinsip:** Creative Idea Suggestion System Toyota (Yasuda, 1991).
- **Preseden:** sistem saran Toyota mengumpulkan sekitar 20 juta ide dalam 40 tahun [Yasuda, 1991].
- **Kekuatan:** memanfaatkan 62% operator yang mau menyumbang ide; murah.
- **Kelemahan:** tanpa kapasitas eksekusi (H, C), ide hanya menumpuk dan tingkat implementasi turun lagi.

### J. Learning-Rate Governance [SISTEM]
- **Prinsip:** kurva belajar (Wright, 1936) dan kaizen costing (Monden, 1995): biaya turun sebagai fungsi pengalaman yang diakumulasi dan dikelola.
- **Kekuatan:** menjawab temuan bahwa pesaing bergerak (benchmark turun sekitar 2,5 poin per tahun); membuat target tidak usang.
- **Kelemahan:** ini cara mengukur dan mengelola, bukan mesin perbaikannya sendiri; tidak cukup sebagai ide utama.

### K. Digital Skill Academy [SISTEM]
- **Prinsip:** Training Within Industry dan belajar sambil membangun.
- **Preseden:** GAIA, akselerator AI grup Toyota dengan akademi software 100+ kursus [Aicadium].
- **Kekuatan:** menutup celah terdalam (Software & AI Level 3+ hanya 2/30) dengan basis mechanical/electrical yang kuat.
- **Kelemahan:** pelatihan saja tidak membuat sinyal kembali; keterampilan yang tidak dipakai akan hilang.

### L. Energy Data Loop [SISTEM]
- **Prinsip:** ISO 50001; energi yang terlihat bisa dikelola.
- **Preseden:** pabrik Nissan di AS meningkatkan kinerja energi 13,8% dalam 3 tahun, 8–21% per pabrik [Clean Energy Ministerial, 2022].
- **Kekuatan:** satu-satunya opsi dengan manfaat lingkungan langsung (energi dan CO₂); menutup celah data energi yang tidak ada di casebook.
- **Kelemahan:** porsi energi hanya sekitar 12% biaya konversi **[ASUMSI]**; dampak biaya kecil bila berdiri sendiri.

## 3. Bagaimana opsi saling menguatkan

| | A | B | C | D | H | I | K | L |
|---|---|---|---|---|---|---|---|---|
| **A Closed-Loop Jidoka** | — | butuh B untuk merutekan sinyal | C membangun model deteksi | D menyimpan penyebab dan solusi | H memberi waktu untuk akar masalah | alert yang diabaikan menjadi input ide | | |
| **B Plug-and-Produce** | membawa sinyal A | — | data terbuka untuk alat C | | | | K mengajarkan standar | membawa data energi |
| **H Firefighting Firewall** | lebih sedikit masalah berulang | | waktu untuk membangun alat | waktu senior untuk sprint | — | kapasitas eksekusi ide | waktu belajar | |

Pola: **A, B, C, D, I, K, L** adalah loop. **H** adalah pemantik yang membuat loop bisa mulai berputar, karena tanpa waktu yang dilindungi semua loop kalah oleh firefighting. **J** adalah cara mengukur apakah loop berputar.

## 4. Ide terintegrasi

### Closed-Loop Kaizen, versi 2

> **Pabrik yang belajar dari dirinya sendiri.** Setiap sinyal kembali ke orang yang bisa bertindak, setiap perbaikan menjadi standar, dan waktu untuk memperbaiki dilindungi agar pabrik keluar dari jebakan firefighting.

| Komponen | Opsi | Prinsip TPS | Apa yang berubah dari versi 1 |
|---|---|---|---|
| Loop kualitas | A (+ G untuk sinyal mesin) | Jidoka | Tidak berubah |
| Loop data & peralatan | B + E + L | Standardized work | Data energi masuk ke loop, menjadi dimensi keberlanjutan |
| Loop manusia & pengetahuan | C + D + I + K | Kaizen, yokoten | Tidak berubah |
| **Pemantik: kapasitas perbaikan yang dilindungi** | **H** | **Kaizen time** | **Baru.** Inilah yang mengubah tiga loop dari proyek menjadi mesin yang berputar sendiri |
| **Ukuran: laju belajar** | **J** | **Genka kaizen** | **Baru.** Target "poin indeks per tahun", dilaporkan terhadap benchmark yang bergerak |

Yang dikeluarkan: **F** (alat, padat modal) dan **G sebagai program terpisah** (sinyalnya masuk ke loop data, tetapi bukan pilar sendiri).

## Cek "done when"

- [x] 12 opsi lintas tuas proses, data, manusia, pengetahuan, peralatan, organisasi.
- [x] Mayoritas opsi adalah perubahan sistem, bukan pembelian (hanya F yang murni BELI).
- [x] Setiap opsi punya preseden publik atau alasan mengapa baru (H: pola capability trap terlihat di Ex.6A).
- [x] Opsi yang saling menguatkan digabung menjadi satu ide terintegrasi.

## Sumber

- Ohno, T. (1988). *Toyota Production System: Beyond Large-Scale Production*. Productivity Press.
- Nakajima, S. (1988). *Introduction to TPM: Total Productive Maintenance*. Productivity Press.
- Repenning, N. P., & Sterman, J. D. (2001). Nobody ever gets credit for fixing problems that never happened. *California Management Review*, 43(4), 64–88.
- Yasuda, Y. (1991). *40 Years, 20 Million Ideas: The Toyota Suggestion System*. Productivity Press.
- Monden, Y. (1995). *Cost Reduction Systems: Target Costing and Kaizen Costing*. Productivity Press.
- Wright, T. P. (1936). Factors affecting the cost of airplanes. *Journal of the Aeronautical Sciences*, 3(4), 122–128.
- Shneiderman, B. (2022). *Human-Centered AI*. Oxford University Press.
- European Commission (2021). *Industry 5.0: Towards a sustainable, human-centric and resilient European industry*.
- Sumber Toyota, Siemens, Kalypso, IIoT World, Omron, Clean Energy Ministerial, Aicadium: lihat tautan di `data/research.md`.
