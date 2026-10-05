# Stage 6 — Roadmap dan Kapabilitas

> Input: keputusan Stage 4 (CLK v2, pilot sealer → inspeksi) dan temuan Stage 5. Pemilik ditulis sebagai **peran di TMMIN**, bukan nama orang. Persentase adalah porsi investasi Rp80 M (pilot-light, sama dengan `model/build_model.py` dan `model/sd_model.py`).

## 1. Prinsip yang ditentukan oleh uji Stage 5

1. **Cepat lebih penting daripada besar.** Terlambat satu tahun membuat peluang NPV positif jatuh ke 21–32%. Semua yang bisa dimulai dengan aset yang ada dimulai pada Q4 2026.
2. **Belanja sedikit sebelum terbukti.** Hanya 25% investasi sebelum gate. Ini asuransi bila loop tidak berhasil: P(NPV>0) tetap 90% vs 60% bila belanja di awal. Preminya sekitar Rp21 M median NPV bila loop berhasil.
3. **Gate di akhir 2027, bukan lebih awal.** KPI orang butuh sekitar 15 bulan data pilot untuk terbaca. Gate pertengahan 2027 menghentikan program yang sebenarnya berhasil.
4. **Lindungi norma, kunci yang dibebaskan.** Waktu perbaikan dilindungi 30% (naik bertahap dalam 6 bulan), dan setiap waktu yang dibebaskan loop dikunci untuk perbaikan (*ratchet*).
5. **Keuntungan tersimpan di cara kerja.** Bila standar dan rutinitas tidak dipelihara setelah 2030, sekitar 6,8 poin indeks biaya hilang dalam lima tahun. Fase 5 (pemeliharaan) adalah bagian dari rencana, bukan tambahan.

## 2. Fase, pemilik, deliverable, dan kriteria lanjut

| Fase | Periode | Investasi | Pemilik | Deliverable | Kriteria lanjut |
|---|---|---|---|---|---|
| **0. Persiapan** | Q4 2026 | 10% (Rp8 M) | Pilot lead: Manajer Body Shop (welding & sealer) | Loop sealer berjalan di kamera CCTV tervalidasi, satu shift; draf standar data v0.1; kanal ide satu ketukan aktif; aturan waktu perbaikan 30% berlaku di area pilot; kohort akademi 1 dimulai | Loop berjalan dan terukur sebelum 31 Des 2026 |
| **1. Pilot** | 2027 | 15% (Rp12 M) | Pilot lead + Pemilik standar data | Loop tertutup di semua shift; 3 alat buatan operator/engineer; 20 item know-how kritis ditangkap dan ditautkan ke standard work; papan abnormalitas team leader | **Gate akhir 2027** (bagian 3) |
| **2. Standardisasi** | 2028 | 40% (Rp32 M) | Pemilik program: Kepala Production Engineering | Yokoten ke final assembly → inspeksi (gelombang 1, Stage 4) dan painting → inspeksi; standar data wajib untuk semua peralatan baru; data mesin masuk ke loop | Standar terbukti di minimal 2 area tambahan; KPI pilot bertahan |
| **3. Roll-out** | 2029 | 25% (Rp20 M) | Pemilik program | Seluruh lini kendaraan Karawang I & II; retrofit peralatan lama sesuai prioritas; data energi per mesin ke team leader | Roll-out sesuai anggaran; kepatuhan alert ≥ 85% di semua lini |
| **4. Skala** | 2030 | 10% (Rp8 M) | Pemilik program + Pemilik standar data | Pabrik mesin Karawang III; perubahan varian lewat konfigurasi; akademi diajar oleh engineer L3 sendiri | Target KPI 2030 (Stage 7) |
| **5. Pelihara** | 2031+ | Penggantian teknologi sekitar Rp16 M/tahun (1/5 per tahun, umur 5 tahun Ex.9) | Direktur Produksi (sponsor) | Standar dan rutinitas loop diaudit tahunan; akademi berjalan sendiri; aturan ratchet tetap berlaku | Indeks biaya tidak naik kembali (peringatan dini: waktu perbaikan < 40%) |

**Sponsor program:** Direktur Produksi. **Pengendali gate:** Controller keuangan pabrik, yang menilai bukti secara independen dari tim pilot.

## 3. Gate go/no-go akhir 2027

Program diskalakan **hanya bila semua kriteria terpenuhi**. Kriteria ini sama dengan target pilot di Stage 7 dan dengan logika gate di kedua model.

| # | Kriteria | Ambang | Baseline | Dasar |
|---|---|---|---|---|
| 1 | Penurunan scrap di area pilot (sealer → inspeksi) | ≥ 60% | 0% | Desain loop 85% (simulasi sealer); 60% = desain × adopsi 80% × kepatuhan 80% |
| 2 | Operator yang mengabaikan alert | ≤ 20% | 31% (Ex.6B) | Kepatuhan ≥ 80% |
| 3 | Adopsi pilot (alert yang ditindaklanjuti sesuai aturan stop/koreksi/eskalasi) | ≥ 80% | — | Gate `model/run_tests.py` |
| 4 | Loop berjalan di semua shift area pilot; area kedua siap | Ya | Tidak | Cakupan ≥ 15% lini di `sd_model.py` |
| 5 | Ide terimplementasi per engineer (laju tahunan) | ≥ 0,75 | 0,67 (Ex.6A) | Bukti bahwa jebakan firefighting mulai terbalik |
| 6 | Waktu engineer untuk perbaikan di area pilot | ≥ 30% | 25% (Ex.6A) | Norma kapabilitas |

**Bila gate gagal:**
- Pilot tetap berjalan dan belanja tahap berikutnya (75%) ditahan.
- Tim menulis A3 tentang penyebab kegagalan.
- Gate dievaluasi ulang setelah 6 bulan.

**Bila semua kriteria terlampaui dengan jelas** (misalnya scrap pilot ≥ 75%, pengabaian alert ≤ 10%), belanja tahap 2 boleh dipercepat. Stage 5 menunjukkan belanja lebih awal bernilai lebih tinggi bila loop terbukti berhasil.

## 4. Seratus hari pertama (hanya aset yang sudah dimiliki TMMIN)

| Hari | Fokus | Aksi | Pemilik |
|---|---|---|---|
| 1–30 | **Lihat** | Genchi genbutsu di sealer → inspeksi bersama operator; baseline scrap, cacat lolos, dan alert yang diabaikan per shift; tetapkan pemilik standar data; luncurkan kanal ide; umumkan aturan waktu perbaikan 30% | Pilot lead |
| 31–60 | **Hubungkan** | Sambungkan kamera AI tervalidasi ke alert di stasiun sealer dan andon digital; rancang aturan alert bersama team leader (alert menjelaskan alasannya); sprint pertama penangkapan know-how dengan senior sealer | Pemilik standar data + team leader |
| 61–100 | **Jalankan** | Loop berjalan di satu shift, lalu semua shift; kaizen mingguan untuk setiap alert yang diabaikan; kohort akademi 1 membangun alat pertamanya; laporan KPI mingguan ke sponsor | Pilot lead + People lead |

Bila kamera AI gagal validasi Oktober 2026, loop tetap berjalan dengan andon digital dan cek operator di stasiun sementara model dilatih ulang. Loop tidak boleh bergantung pada satu sensor.

## 5. Rencana kapabilitas

| Siapa | Belajar apa | Seberapa cepat | Bagaimana pengetahuan ditangkap |
|---|---|---|---|
| Engineer (30 per bidang, Ex.7) | Software & AI: dari L1/L2 ke L3 lewat kohort berjenjang; setiap kohort membangun satu alat nyata di pilot | L1→L2 30%/tahun, L2→L3 20%/tahun; L3+ dari 2 menjadi **13,6 pada akhir 2030** (`sd_model.py`; spreadsheet sekitar 14) | Kode dan model disimpan di platform internal dengan dokumentasi standar; engineer L3 mengajar mulai 2029 |
| Operator | Membaca dan menindaklanjuti alert; mencatat ide; alat berbasis data sederhana | Terlatih dari 18% ke 50% (2027) dan 90% (2030) | Alert yang diabaikan menjadi input kaizen; ide kecil langsung dieksekusi team leader |
| Team leader | Menyetel aturan alert; memimpin kaizen harian; papan abnormalitas | Seluruh team leader area pilot pada 2027 | Aturan alert adalah bagian standard work |
| Senior (pemilik know-how kritis) | Menjadi validator, bukan satu-satunya sumber jawaban | Sprint terjadwal; 12% dari know-how yang belum terdokumentasi per tahun | Wawancara berbantuan AI, divalidasi ahli, ditautkan ke standard work (O-Beya lantai pabrik) |

**Aturan waktu (dari Stage 5):**
- Waktu perbaikan minimal 30% untuk engineer dan team leader di area yang sudah masuk program, naik bertahap dalam 6 bulan.
- Setiap jam yang dibebaskan loop dikunci untuk perbaikan dan tidak dialihkan ke tugas rutin baru (ratchet).
- Pelanggaran aturan dilaporkan ke sponsor seperti pelanggaran keselamatan.

## 6. Bangun sendiri vs bermitra

| Komponen | Pilihan | Alasan |
|---|---|---|
| Logika loop dan aturan alert | Bangun | Know-how inti, terikat ke standard work |
| Standar antarmuka dan data pabrik | Bangun | Kepemilikan inilah yang memangkas bulan per varian |
| Model inspeksi AI | Bangun | Melanjutkan kamera CCTV in-house |
| Peralatan dan fixture standar | Bangun | Lebih murah, fleksibel, memakai engineer sendiri |
| Komputasi dan cloud | Mitra | Komoditas |
| Pembangunan loop pertama di pilot | Mitra, sementara | `sd_model.py` mengasumsikan dukungan mitra hanya selama pilot; setelah itu laju rollout bergantung pada engineer L3+ sendiri |
| Sensor canggih, proses baterai | Mitra | Teknologi khusus |

**Aturan transfer pengetahuan untuk setiap kontrak mitra:**
1. Setiap engineer mitra berpasangan dengan engineer TMMIN.
2. Semua hasil didokumentasikan dalam standar data TMMIN.
3. Serah terima dan demonstrasi oleh engineer TMMIN menjadi syarat pembayaran akhir.
4. Tidak ada antarmuka tertutup milik mitra.

## 7. Risk register

| Risiko | Peluang (1–5) | Dampak (1–5) | Skor | Mitigasi | Indikator peringatan dini | Pemilik |
|---|---|---|---|---|---|---|
| Penghematan terlambat (pilot lambat dimulai) | 3 | 5 | 15 | 100 hari pertama dengan aset yang ada; tinjauan KPI mingguan | Loop belum berjalan 31 Des 2026 | Pilot lead |
| Operator tidak percaya atau mengabaikan alert | 4 | 5 | 20 | Alert dirancang bersama team leader dan menjelaskan alasannya; setiap pengabaian dibahas di kaizen | Tingkat pengabaian alert (31% hari ini) | Team leader |
| Loop tidak berhasil di konteks TMMIN (adopsi rendah) | 2 | 5 | 10 | Pilot-light + gate: 75% belanja ditahan | Scrap pilot < 60% pada Q3 2027 | Controller (gate) |
| Kinerja memburuk dulu sebelum membaik (waktu perbaikan dilindungi saat firefighting masih tinggi) | 3 | 3 | 9 | Perlindungan hanya pada norma 30%, naik bertahap dalam 6 bulan; kapasitas firefighting cadangan di 2027 | Masalah tidak tertangani > 15% (`sd_model.py`: puncak sekitar 11% pada Q2 2027) | Pemilik program |
| Rollout tertahan karena engineer L3+ kurang | 4 | 4 | 16 | Akademi mulai Q4 2026; mitra hanya untuk pilot dengan transfer pengetahuan | Engineer L3+ < 4 di akhir 2027 (rencana 4,9) | People lead |
| Integrasi peralatan lama sulit | 4 | 4 | 16 | Standar wajib untuk peralatan baru; retrofit bertahap | Porsi peralatan pilot pada standar | Pemilik standar data |
| Kompleksitas varian naik lebih cepat dari asumsi | 3 | 3 | 9 | Standar data mengubah varian menjadi konfigurasi; justru menaikkan nilai program (tornado: NPV naik) | Jumlah varian baru per tahun | Pemilik program |
| Keuntungan hilang setelah 2030 (standar tidak dipelihara) | 3 | 4 | 12 | Fase 5: audit tahunan, penggantian teknologi dianggarkan, ratchet tetap berlaku | Waktu perbaikan < 40%; indeks biaya naik 2 kuartal berturut-turut | Sponsor |
| Senior tidak punya waktu berbagi know-how | 3 | 3 | 9 | Sprint terlindungi; pengakuan; wawancara berbantuan AI | Porsi know-how terdokumentasi | People lead |
| Kamera AI gagal validasi Oktober 2026 | 2 | 4 | 8 | Andon digital dan cek operator sementara model dilatih ulang | Akurasi validasi terhadap ambang | Pemilik standar data |

## Cek "done when"

- [x] Setiap fase punya pemilik, deliverable, dan kriteria lanjut.
- [x] Gate dengan kriteria terukur sebelum belanja besar (25% sebelum gate).
- [x] 100 hari pertama hanya memakai aset yang ada.
- [x] Rencana kapabilitas, aturan build/partner dengan transfer pengetahuan, dan risk register dengan KPI peringatan dini.
