# Cara memakai folder ini di Claude Code

1. Ekstrak zip, lalu buka folder `bcc-tmmin` di Claude Code (terminal: `cd bcc-tmmin && claude`, atau buka foldernya di aplikasi desktop).
2. Claude otomatis membaca `CLAUDE.md` (konteks kasus) dan menemukan skill `case-solution-design`.
3. Contoh perintah:
   - "Pakai skill case-solution-design, jalankan Stage 2 dan buat issue tree baru."
   - "Ubah asumsi scrap jadi 30%, jalankan ulang model dan simulasi, lalu update angka di proposal."
   - "Buat 20 pertanyaan juri beserta jawabannya (Stage 8)."
4. Untuk menjalankan model: `pip install openpyxl numpy`, lalu `cd model && python build_model.py && python run_tests.py`.

## Skill yang terpasang

| Skill | Fungsi | Cara panggil |
|---|---|---|
| `case-solution-design` | Alur 8 tahap mengerjakan kasus | "pakai case-solution-design, Stage 3" |
| `judge-panel` | Menguji solusi dari 4 sudut pandang juri, lalu membuat bank Q&A (hemat token) | "jalankan judge-panel" |
| `mckinsey-strategy-team` | Tim agen: beberapa agen membuat opsi tandingan, lalu panel penguji menyerang rekomendasi. Sangat kuat tapi boros token. Pakai sekali saja di akhir | "/mckinsey-strategy-team pressure-test rekomendasi kami" (perlu `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1`) |
| `verification-before-completion` | Claude wajib menjalankan ulang skrip sebelum mengklaim angka benar | otomatis |
| `concise` | Jawaban chat lebih pendek (sekitar 60–70% lebih hemat), tetap enak dibaca | "/concise" |
| `caveman` | Mode paling hemat (sekitar 65%), kalimat sangat ringkas | "/caveman", berhenti dengan "normal mode" |

## Penghemat token lain

- **`.claude/settings.json`** memblokir Claude membaca file berat (xlsx, pdf, docx, gambar). Angka diambil dengan menjalankan skrip.
- **Aturan di `CLAUDE.md`:** cari dulu dengan grep, lalu baca baris yang perlu saja.
- **Tips:**
  - Ketik `/clear` setiap ganti tugas besar.
  - Ketik `/compact` kalau percakapan sudah panjang.
  - Satu sesi untuk satu Stage.

Sumber dan lisensi skill dari GitHub ada di `.claude/skills/THIRD_PARTY.md`.

Isi folder:
- `data/` — masalah, fakta casebook, riset, ideation
- `model/` — workbook Excel, skrip model, skrip simulasi
- `outputs/` — draf proposal, grafik, template Word
