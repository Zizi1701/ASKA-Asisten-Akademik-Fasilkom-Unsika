# 🤖 Chatbot Akademik RAG - Sistem Cerdas

Repositori ini berisi proyek Ujian Akhir Semester (UAS) mata kuliah Sistem Cerdas. Proyek ini adalah sebuah Asisten Cerdas (Chatbot) Akademik untuk mahasiswa Sistem Informasi yang dibangun menggunakan arsitektur **Retrieval-Augmented Generation (RAG)**.

Chatbot ini dirancang untuk menjawab pertanyaan seputar jadwal akademik, aturan pengisian KRS, panduan skripsi, hingga regulasi magang secara cepat, akurat, dan faktual berdasarkan dokumen resmi kampus.

## ✨ Fitur Utama

- **Anti-Halusinasi**: Chatbot hanya akan menjawab berdasarkan konteks yang ada di dalam buku pedoman resmi. Jika informasi tidak ditemukan, bot akan merespons dengan jujur.
- **Pencarian Cerdas (Semantic Search)**: Menggunakan model _Embedding_ Multilingual untuk memahami makna dari pertanyaan berbahasa Indonesia, bukan sekadar mencocokkan kata kunci.
- **Sitasi Transparan**: Setiap jawaban yang diberikan akan menyertakan sumber referensi (nomor halaman dan kutipan asli) dari dokumen PDF terkait.
- **Local Vector Database**: Dokumen diproses dan disimpan secara luring (_offline_) menggunakan FAISS untuk mempercepat waktu respons dan menghemat biaya API.

## 🛠️ Teknologi yang Digunakan

- **Bahasa Pemrograman**: Python 3
- **LLM**: Google Gemini API (`gemini-2.5-flash`)
- **Embedding Model**: HuggingFace (`sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`)
- **Vector Store**: FAISS (Facebook AI Similarity Search)
- **Framework**: LangChain

## 📁 Struktur Direktori

```text
CHATBOTAKADEMIK/
│
├── data/                               # Folder berisi file PDF pedoman akademik kampus
├── env/                                # Virtual Environment Python
├── vectorstore/
│   └── faiss_index/                    # Folder penyimpanan database vektor hasil embedding
│
├── .env                                # File rahasia untuk menyimpan kredensial API Key
├── .gitignore                          # Daftar file dan folder yang diabaikan oleh Git
├── chatbot.py                          # Skrip utama logika RAG dan antarmuka Chatbot
├── ingest_data.py                      # Skrip untuk mengekstrak teks PDF dan membuat Vector Database
└── requirements.txt                    # Daftar library Python yang dibutuhkan proyek
```

## 🚀 Cara Menjalankan Proyek

### 1️⃣ Kloning Repositori

Unduh kode sumber ke komputer Anda:

```bash
git clone https://github.com/muhiqballz/Chatbot-Akademik-RAG.git
cd Chatbot-Akademik-RAG
```

---

### 2️⃣ Siapkan Virtual Environment

Disarankan menggunakan virtual environment agar dependensi terisolasi.

#### 🪟 Windows:

```bash
python -m venv env
.\env\Scripts\activate
```

#### 🍎 Mac/Linux:

```bash
python3 -m venv env
source env/bin/activate
```

💡 **Catatan:** Pastikan muncul `(env)` di terminal sebagai tanda environment aktif.

---

### 3️⃣ Instalasi Dependensi

Instal semua library yang dibutuhkan:

```bash
pip install -r requirements.txt
```

---

### 4️⃣ Konfigurasi API Key (Google Gemini)

Buat file `.env` di folder utama proyek, lalu isi dengan:

```
GEMINI_API_KEY=masukkan_api_key_gemini_anda_di_sini
```

---

### 5️⃣ Membangun Database Pengetahuan (Ingest Data)

Jalankan perintah berikut untuk memproses file PDF menjadi vector database (FAISS):

```bash
python ingest_data.py
```

⚠️ **Penting:**

- Hanya perlu dijalankan sekali di awal
- Jalankan ulang jika ada perubahan/penambahan file PDF di folder `data/`

---

### 6️⃣ Jalankan Chatbot (Terminal) 🎉

Mulai chatbot dan lakukan percakapan:

```bash
python chatbot.py
```

---

### 7️⃣ Jalankan Web Chatbot 🎉

Mulai web chatbot dan lakukan percakapan:

```bash
streamlit run app.py
```

---

## 🧠 Teknologi yang Digunakan

- LangChain
- FAISS (Vector Database)
- Google Gemini API
- Python

---

## 📌 Catatan

Pastikan koneksi internet aktif saat menggunakan chatbot karena membutuhkan akses ke API Google Gemini.
