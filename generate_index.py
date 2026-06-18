import os
from dotenv import load_dotenv
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter, CharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

load_dotenv()

def create_vector_db():
    print("1. Memulai proses ingesti data per file...")
    data_dir = "data/" 

    if not os.path.exists(data_dir):
        print(f"❌ Error: Folder tidak ditemukan di '{data_dir}'")
        return

    all_chunks = []

    # Daftar konfigurasi untuk masing-masing file
    file_configs = [
        {
            "filename": "Daftar Dosen Fasilkom Unsika.txt",
            "kategori": "dosen",
            "tipe": "tabular"
        },
        {
            "filename": "Jadwal Kelas Fasilkom Unsika.txt",
            "kategori": "jadwal",
            "tipe": "tabular"
        },
        {
            "filename": "Kalender Akademik Unsika.txt",
            "kategori": "kalender",
            "tipe": "tabular"
        },
        {
            "filename": "Panduan Magang Sistem Informasi Unsika.txt",
            "kategori": "magang",
            "tipe": "naratif"
        },
        {
            "filename": "Panduan Tugas Akhir Fasilkom Unsika.txt",
            "kategori": "ta",
            "tipe": "naratif"
        }
    ]

    # --- DEFINISI TEXT SPLITTER ---
    tabular_splitter = CharacterTextSplitter(
        separator="\n",
        chunk_size=5000,
        chunk_overlap=0
    )

    naratif_splitter = RecursiveCharacterTextSplitter(
        separators=[
            "================================================================================",
            "--------------------------------------------------------------------------------",
            "\n\n",
            "\n",
            ".",
            " "
        ],
        chunk_size=1200,
        chunk_overlap=250
    )

    # --- PROSES LOADING & CHUNKING ---
    for config in file_configs:
        filepath = os.path.join(data_dir, config["filename"])
        
        if not os.path.exists(filepath):
            print(f"⚠️ Peringatan: File {config['filename']} tidak ditemukan, dilewati.")
            continue
            
        try:
            loader = TextLoader(filepath, encoding='utf-8')
            documents = loader.load()
            
            for doc in documents:
                doc.metadata["kategori"] = config["kategori"]
                doc.metadata["source"] = config["filename"]
                
            if config["tipe"] == "tabular":
                chunks = tabular_splitter.split_documents(documents)
            else:
                chunks = naratif_splitter.split_documents(documents)
                
            all_chunks.extend(chunks)
            print(f"   ✅ Berhasil memproses {config['filename']} -> {len(chunks)} chunks.")
            
        except Exception as e:
            print(f"❌ Error membaca {config['filename']}: {e}")

    if len(all_chunks) == 0:
        print("❌ Tidak ada dokumen .txt yang terbaca atau gagal di-chunking.")
        return

    print(f"\n2. Total keseluruhan dokumen setelah dipecah: {len(all_chunks)} chunks")
    print("3. Membuat embeddings dengan model Bahasa Indonesia...")
    
    # Model ini sudah benar untuk Bahasa Indonesia
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")

    print("4. Menyimpan ke FAISS...")
    vectorstore = FAISS.from_documents(all_chunks, embeddings)
    os.makedirs("vectorstore", exist_ok=True)
    vectorstore.save_local("vectorstore/faiss_index")
    print("✅ Selesai! Vectorstore berhasil menyimpan semua dokumen.")

if __name__ == "__main__":
    create_vector_db()