import os
from dotenv import load_dotenv
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_classic.chains import create_retrieval_chain
from langchain_classic.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate

def jalankan_chatbot():
    load_dotenv()
    if not os.getenv("GEMINI_API_KEY"):
        print("❌ GEMINI_API_KEY tidak ditemukan di .env!")
        return

    if not os.path.exists("vectorstore/faiss_index"):
        print("❌ Vectorstore belum ada! Jalankan dulu: python ingest_data.py")
        return

    print("🚀 Memuat vectorstore...")
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")
    vectorstore = FAISS.load_local("vectorstore/faiss_index", embeddings, allow_dangerous_deserialization=True)
    
    # MODIFIKASI 1: Menggunakan MMR agar pencarian menyebar ke berbagai PDF (tidak tertutup file besar)
    retriever = vectorstore.as_retriever(search_type="mmr", search_kwargs={"k": 6, "fetch_k": 20})

    print("🤖 Menyiapkan LLM Google Gemini...")
    llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0)

    system_prompt = (
        "Kamu adalah asisten akademik kampus yang sangat cerdas dan ramah. "
        "Gunakan HANYA potongan konteks dokumen berikut untuk menjawab pertanyaan mahasiswa. "
        "Jika jawabannya tidak ada di dalam konteks, katakan dengan jujur: "
        "'Maaf, saya tidak menemukan informasi tersebut di dalam buku pedoman kampus.' "
        "Jangan pernah mengarang jawaban dari luar dokumen.\n\n"
        "Konteks Dokumen:\n{context}"
    )

    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", "{input}"),
    ])

    rag_chain = create_retrieval_chain(
        retriever,
        create_stuff_documents_chain(llm, prompt)
    )

    print("\n" + "=" * 50)
    print("🤖 Chatbot Siap! (Ketik 'keluar' untuk berhenti)")
    print("=" * 50)

    while True:
        pertanyaan = input("\nMahasiswa: ").strip()

        if pertanyaan.lower() in ['keluar', 'exit', 'quit']:
            print("Sampai jumpa! 👋")
            break

        if not pertanyaan:
            continue

        print("⏳ Mencari di buku panduan...")

        try:
            response = rag_chain.invoke({"input": pertanyaan})
            print("\n🤖 Chatbot:")
            print(response["answer"])
            print("\n📚 [Sumber]:")
            for doc in response["context"]:
                halaman = doc.metadata.get('page', '?')
                
                # MODIFIKASI 2: Menarik nama file asli dari metadata
                nama_file = os.path.basename(doc.metadata.get('source', 'Dokumen Tidak Diketahui'))
                
                kutipan = doc.page_content[:120].replace('\n', ' ')
                
                # Cetak nama file beserta halamannya
                print(f"  - {nama_file} (Halaman {halaman}): \"{kutipan}...\"")
        except Exception as e:
            print(f"\n❌ Error: {e}")

if __name__ == "__main__":
    jalankan_chatbot()