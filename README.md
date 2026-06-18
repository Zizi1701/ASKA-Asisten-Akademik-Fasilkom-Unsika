# 🤖 ASKA - Asisten Akademik Fasilkom UNSIKA

ASKA adalah Chatbot cerdas berbasis **RAG (Retrieval-Augmented Generation)** yang dirancang untuk menjawab pertanyaan seputar akademik di Fakultas Ilmu Komputer (Fasilkom) UNSIKA.

Aplikasi ini dibangun menggunakan **FastAPI** sebagai backend, **LangChain** & **FAISS** untuk pemrosesan dokumen (vektor), dan ditenagai oleh model LLM **Google Gemini 2.5 Flash**.

---

## ✨ Fitur Utama

- **Pencarian Semantik:** Memahami konteks pertanyaan (bukan sekadar pencocokan kata) menggunakan model embedding Multilingual.
- **Hybrid/MMR Search:** Mampu mencari data secara merata di berbagai dokumen berbeda (Tabel Dosen, Jadwal Kelas, Panduan Magang, dll).
- **Riwayat Percakapan (Memory):** Chatbot mampu mengingat konteks pertanyaan sebelumnya.
- **Frontend Responsif:** Antarmuka obrolan yang bersih dan modern menggunakan HTML & TailwindCSS.

---

## 🛠️ Persyaratan Sistem (Prerequisites)

Sebelum menjalankan proyek ini, pastikan komputermu sudah menginstal:

1. **Python 3.8** atau versi lebih baru.
2. **Git** (Opsional, untuk proses cloning).
3. **Gemini API Key** (Dapatkan secara gratis dari [Google AI Studio](https://aistudio.google.com/)).

---

## 🚀 Cara Menjalankan Aplikasi Secara Lokal (Step-by-Step)

Ikuti langkah-langkah di bawah ini secara berurutan untuk menjalankan ASKA di komputermu:

1. Clone Repositori
Buka terminal/Command Prompt, lalu jalankan perintah ini:

```bash
git clone [https://github.com/username-kamu/nama-repositori-kamu.git](https://github.com/username-kamu/nama-repositori-kamu.git)
cd nama-repositori-kamu
(Ganti URL di atas dengan link repository GitHub milikmu).

2. Buat Virtual Environment (Sangat Disarankan)
Agar library yang diinstal tidak mengganggu sistem Python komputermu, buat lingkungan virtual:
Untuk Windows:

Bash
python -m venv env
env\Scripts\activate
Untuk Mac/Linux:

Bash
python3 -m venv env
source env/bin/activate
3. Instal Library yang Dibutuhkan
Pastikan kamu sudah berada di dalam virtual environment, lalu instal semua dependensi dari file requirements.txt:

Bash
pip install -r requirements.txt
4. Konfigurasi API Key (.env)
Buat file baru bernama .env di folder utama proyek (sejajar dengan api.py).

Buka file .env tersebut dan masukkan Gemini API Key milikmu dengan format seperti ini:

Cuplikan kode
GEMINI_API_KEY=masukkan_api_key_kamu_disini
5. Buat Database FAISS (Ingestion)
PENTING! Langkah ini wajib dilakukan pertama kali agar chatbot memiliki "otak/pengetahuan" dari dokumen Fasilkom.
Jalankan script pembuat database:

Bash
python ingest_data.py
(Tunggu prosesnya hingga selesai dan muncul keterangan bahwa Vectorstore berhasil dibuat. Ini akan memunculkan folder vectorstore/faiss_index).

6. Jalankan Server FastAPI
Setelah database berhasil dibuat, nyalakan server backend:

Bash
uvicorn api:app --reload
7. Buka Frontend ASKA
Jika server sudah menyala (ditandai dengan keterangan Application startup complete di terminal), silakan buka browser dan akses alamat berikut:
👉 http://127.0.0.1:8000

Selamat! ASKA sudah siap digunakan untuk menjawab seputar akademik Fasilkom UNSIKA. 🎉

📁 Struktur Direktori
/data/ : Folder tempat meletakkan file .txt atau dokumen sumber (jadwal, daftar dosen, panduan).

/vectorstore/ : Folder hasil ekstraksi FAISS (akan muncul setelah menjalankan ingest_data.py).

api.py : Kode utama untuk backend server FastAPI dan konfigurasi rantai RAG LangChain.

ingest_data.py : Script untuk membaca dokumen /data dan mengubahnya menjadi vektor (embedding).

index.html : Halaman antarmuka web (UI) untuk ngobrol dengan chatbot.


***

### Cara menggunakannya:
1. Buka file `README.md` di proyek VSCode kamu.
2. Timpa (replace) semua isinya dengan teks di atas.
3. Ingat untuk mengubah bagian `[https://github.com/username-kamu/nama-repositori-kamu.git](https://github.com/username-kamu/nama-repositori-kamu.git)` di Langkah 1 dengan URL asli repositori GitHub kamu.
4. Jangan lupa **Save (Ctrl+S)** dan *push* ulang ke GitHub!
```
