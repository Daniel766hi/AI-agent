# Research

## Preseden Toyota (bukti bahwa arah ini nyata)

| Inisiatif | Apa yang dilakukan | Angka | Sumber |
|---|---|---|---|
| Toyota AI Platform | Staf pabrik membuat model machine learning sendiri tanpa coding (inspeksi, adhesive, abnormalitas mesin injeksi) | ~10.000 model; >10.000 jam kerja/tahun dihemat; ~1.200 pengguna aktif; 400+ peserta pelatihan/tahun | [Google Cloud](https://cloud.google.com/blog/topics/hybrid-cloud/toyota-ai-platform-manufacturing-efficiency), [Chief AI Officer](https://chiefaiofficer.com/blog/how-toyota-gave-ai-tools-to-factory-workers-and-saved-10000-hours/) |
| O-Beya | Sistem AI generatif dengan 9 agen spesialis untuk menyimpan pengetahuan engineer senior yang pensiun | ~800 engineer powertrain | [Microsoft](https://news.microsoft.com/source/asia/features/toyota-is-deploying-ai-agents-to-harness-the-collective-wisdom-of-engineers-and-innovate-faster/), [ABI Research](https://www.abiresearch.com/market-research/insight/7786905-toyotas-o-beya-provides-best-practices-for) |
| GAIA | Akselerator AI grup Toyota (2025), berakar pada prinsip jidoka; akademi software 100+ kursus | 11 kategori | [Aicadium](https://aicadium.ai/lean-to-ai-what-toyotas-transformation-looks-like-today/) |
| Pabrik BEV generasi berikut | Self-propelled assembly line, gigacasting, verifikasi proses digital | Target: lead time persiapan dan investasi pabrik turun 50% | [Toyota](https://global.toyota/en/newsroom/corporate/39330500.html), [Toyota Monozukuri](https://global.toyota/en/newsroom/corporate/39758451.html) |

## Benchmark untuk asumsi penghematan

| Tuas | Benchmark | Asumsi kami | Sumber |
|---|---|---|---|
| Predictive maintenance | Biaya perawatan −18 s.d. 25%; downtime hingga −50% (McKinsey) | −10% (lebih konservatif) | [IIoT World](https://www.iiot-world.com/predictive-analytics/predictive-maintenance/predictive-maintenance-cost-savings/) |
| Virtual commissioning | Commissioning di lokasi −70% pada lini mesin 17 varian (Wipro PARI); hingga −40% (Kalypso) | Biaya modifikasi varian −35% | [Siemens](https://resources.sw.siemens.com/en-US/case-study-wipro-pari/), [Kalypso](https://kalypso.com/viewpoints/entry/reducing-commissioning-time-by-40-with-a-digital-twin) |
| Manajemen energi | Kinerja energi +13,8% dalam 3 tahun (Nissan AS, 8–21% per pabrik) | −5% | [Clean Energy Ministerial](https://www.cleanenergyministerial.org/content/uploads/2022/03/cem-em-casestudy-nissan-usa.pdf) |
| Intralogistik AMR | Hingga 15 km jalan kaki/hari per pekerja dihilangkan | Waktu NVA operator −30% (dicek dengan time study) | [Omron](https://robotics.omron.com/case-studies/amr-automation-intralogistics-mpa-omron/) |

## Bacaan konsep (TPS × AI, human-centered)

- [The Future Factory: TPS in the Age of AI](https://www.thefuturefactory.com/insights/toyota-production-system-age-of-ai) — kaizen menstabilkan proses dulu agar data bisa dipercaya
- [Sendfull: What Toyota Can Teach Us About AI Automation](https://sendfull.substack.com/p/ep-81-what-toyota-can-teach-us-about) — TPS dirancang untuk intervensi manusia, bukan ketiadaan manusia
- [Lean Tomatoes: Toyota using AI to reinvent kaizen](https://leantomatoes.com/2025/11/19/toyota-using-ai-to-reinvent-kaizen-and-boost-productivity/)
- [DigitalDefynd: 10 ways Toyota is using AI](https://digitaldefynd.com/IQ/toyota-using-ai-case-study/)
- Industry 5.0 (European Commission, 2021) dan Human-Centered AI (Shneiderman) untuk dasar akademis

## Hasil simulasi tim

**Tes 1 — Closed loop vs kamera saja (drift sealer, 175.000 unit, 300 simulasi)**

| Skenario | Indeks scrap area pilot |
|---|---|
| Saat ini (inspeksi visual di akhir) | 100 |
| Kamera lebih baik di akhir lini saja | 112 |
| Closed loop, 31% alert diabaikan | 34 |
| Closed loop dengan desain berpusat manusia | 15 |

Temuan: kamera saja menaikkan scrap karena cacat tetap ditemukan terlambat. Kepercayaan operator bernilai: alert yang diabaikan menghilangkan seperlima manfaat. Penurunan terendah di semua uji sensitivitas sekitar 80%.

**Tes 2 — Uji stres finansial (10.000 simulasi, 13 input tidak pasti)** — dijalankan ulang Oktober 2026; angka di bawah adalah output `model/run_tests.py` saat ini

| Strategi | Peluang NPV > 0 | NPV kasus buruk (P5) |
|---|---|---|
| Belanja di awal, tanpa gate | 49% | −Rp32,8 M |
| Pilot-light, tanpa gate | 73% | −Rp19,4 M |
| **Pilot-light + gate 2027 (rencana kami)** | **86%** | **−Rp8,4 M** |
| Rencana kami, penghematan terlambat 1 tahun | 32% | −Rp31,9 M |
| Terlambat 1 tahun, nilai sisa peralatan dihitung | 88% | −Rp3,8 M |

**Tes 3 — Tornado:** input paling berpengaruh ke NPV adalah besar investasi, tingkat adopsi, dan penurunan scrap.

**Tes 4 — Model system dynamics (`model/sd_model.py`):** lihat `work/5_tests.md`. Ringkas: indeks biaya 2030 pada harga konstan 2025 100,8 (vs 113,9 tanpa tindakan); NPV Rp31,4 M vs tanpa tindakan; P(NPV>0) 94%; terlambat 1 tahun 21%; CO₂ dihindari 1.765 t/tahun pada 2030.

## Repo GitHub yang bisa dipakai

| Repo | Kegunaan |
|---|---|
| [moxlos/process-flow-simulator](https://github.com/moxlos/process-flow-simulator) | Simulasi lini perakitan (SimPy + Streamlit) untuk line balancing dan throughput |
| [GitHub topic: simpy](https://github.com/topics/simpy?o=desc&s=updated) | Digital twin lini produksi, deteksi bottleneck |
| [AndreasKuhnle/SimRLFab](https://github.com/AndreasKuhnle/SimRLFab) | Simulasi dan reinforcement learning untuk perencanaan produksi |
| [tusharraju7/CaseCompetition_Decks](https://github.com/tusharraju7/CaseCompetition_Decks) | Contoh deck pemenang case competition (struktur dan polish) |
| [GitHub topic: case-competition](https://github.com/topics/case-competition) | 17 submission case competition lain |

## Tips memenangkan case competition

- Satu rekomendasi yang jelas, didukung analisis terstruktur dan tiga langkah aksi ([Management Consulted](https://managementconsulted.com/how-to-win-a-case-competition/))
- Judul slide harus bisa dibaca sebagai satu cerita utuh
- Akui opsi lain lalu jelaskan kenapa solusi kita lebih baik ("inoculating the judges") ([Wharton](https://www.wharton.upenn.edu/story/how-these-wharton-undergrads-won-the-world-championship-of-case-competitions/))
- Estimasi biaya, penghematan, dan ROI walau kasar menunjukkan kematangan bisnis ([Hacking the Case Interview](https://www.hackingthecaseinterview.com/pages/case-competitions))
