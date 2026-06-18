import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List, Optional
from dotenv import load_dotenv

# LangChain Imports
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains import create_retrieval_chain, create_history_aware_retriever
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage

load_dotenv()

app = FastAPI(title="ASKA API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- STARTUP: Memuat model saat server baru menyala ---
print("Initializing ASKA Knowledge Base...")

# 1. Model Embedding 
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")
vectorstore = FAISS.load_local("vectorstore/faiss_index", embeddings, allow_dangerous_deserialization=True)

# 2. Retriever: Mengambil 20 chunks agar konteks sangat kaya
retriever = vectorstore.as_retriever(
    search_type="mmr", 
    search_kwargs={"k": 15, "fetch_k": 50}
)

# 3. LLM Setup 
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash", 
    temperature=0,
    google_api_key=os.getenv("GEMINI_API_KEY")
)

# 4. ADVANCED: Contextualize Prompt untuk History & Pembersihan Query
# Membuang sapaan 'Pak'/'Bu' agar Semantic Search FAISS lebih akurat
ctx_prompt = ChatPromptTemplate.from_messages([
    ("system",
     "Mengingat riwayat obrolan dan pertanyaan terbaru pengguna, formulasikan pertanyaan mandiri (standalone question). "
     "PENTING: Jika pengguna menanyakan data spesifik dengan sapaan (contoh: 'nidn pak apriade' atau 'jadwal bu fida'), "
     "hilangkan sapaan 'pak' atau 'bu' tersebut agar menjadi kata kunci pencarian yang bersih (contoh: 'NIDN Apriade' atau 'Jadwal Fida'). "
     "JANGAN menjawab pertanyaan, cukup formulasikan ulang saja."),
    MessagesPlaceholder("chat_history"),
    ("human", "{input}"),
])
history_aware_retriever = create_history_aware_retriever(llm, retriever, ctx_prompt)

# 5. ADVANCED: System Prompt (Anti Markdown & Pencocokan Nama Fleksibel)
system_prompt = """Kamu adalah asisten akademik resmi Fasilkom UNSIKA yang cerdas. 
Gunakan HANYA potongan konteks dokumen berikut untuk menjawab pertanyaan. 

ATURAN MENJAWAB:
1. FORMATTING: JANGAN gunakan tanda bintang ganda (**) untuk menebalkan teks. Gunakan teks biasa yang rapi.
2. MEMBACA DATA DOSEN (PENTING): Data dosen mungkin berasal dari potongan tabel. Jika pengguna menanyakan NIDN atau NIP, dan kamu melihat deretan angka (biasanya 8-10 digit untuk NIDN, atau 18 digit untuk NIP) di sebelah atau di dekat nama dosen tersebut, MAKA ANGKA TERSEBUT ADALAH NIDN/NIP-NYA (meskipun tidak ada kata "NIDN" di baris itu).
3. NAMA DOSEN: Fleksibel dalam mencocokkan nama. Jika ditanya "Pak Apriade", carilah nama yang paling mirip (misal: "Apriade Voutama").
4. JADWAL: Sebutkan Hari, Jam, Kelas, Mata Kuliah, Dosen, dan Ruang secara lengkap.
5. Jika nama yang dicari memang sama sekali tidak ada di dalam konteks, barulah katakan: 'Maaf, saya tidak menemukan informasi tersebut di dalam dokumen pedoman Fasilkom.'

Konteks Dokumen:
{context}"""

qa_prompt = ChatPromptTemplate.from_messages([
    ("system", system_prompt),
    MessagesPlaceholder("chat_history"),
    ("human", "{input}"),
])

rag_chain = create_retrieval_chain(
    history_aware_retriever, 
    create_stuff_documents_chain(llm, qa_prompt)
)
print("ASKA Initialized and ready!")

# --- ENDPOINTS ---

@app.get("/favicon.png", include_in_schema=False)
async def get_favicon():
    return FileResponse("Asisten Akademik Fasilkom Unsika.png")

@app.get("/health")
async def health_check():
    return {"status": "ok"}

class Message(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    pesan: str
    history: Optional[List[Message]] = []

@app.post("/chat")
async def chat_endpoint(req: ChatRequest):
    try:
        # Mengonversi history dari frontend ke format LangChain
        chat_history = [
            HumanMessage(content=m.content) if m.role == "user" else AIMessage(content=m.content)
            for m in (req.history or [])[-6:]
        ]

        # Menjalankan RAG Chain
        resp = rag_chain.invoke({"input": req.pesan, "chat_history": chat_history})
        
        # --- DEBUGGING TERMINAL ---
        print(f"\n[USER]: {req.pesan}")
        konteks_diambil = resp.get("context", [])
        print(f"[DEBUG] Berhasil mengambil {len(konteks_diambil)} potongan dokumen.")
        for i, doc in enumerate(konteks_diambil[:3]): # Print 3 teratas saja
            nama_file = os.path.basename(doc.metadata.get("source", "Dokumen"))
            print(f"  -> Chunk {i+1} dari {nama_file}")
        print("=============================================\n")
        
        # Format Jawaban
        jawaban = resp["answer"]
        sumber = list(set([os.path.basename(doc.metadata.get("source", "Dokumen")) for doc in resp.get("context", [])]))
        
        return {"status": "success", "jawaban": jawaban, "sumber": sumber}
    except Exception as e:
        return {"status": "error", "message": str(e)}