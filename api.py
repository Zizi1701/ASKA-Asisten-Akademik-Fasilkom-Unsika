from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import os
import csv
from datetime import datetime
from dotenv import load_dotenv
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains import create_retrieval_chain, create_history_aware_retriever
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage

# Load environment variables
load_dotenv()

app = FastAPI(title="ASKA API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from fastapi.responses import FileResponse

@app.get("/")
async def read_index():
    return FileResponse("index.html")

# --- GLOBAL VARIABLES UNTUK LAZY LOADING ---
_embeddings = None
_vectorstore = None
_rag_chain = None

def get_rag_chain():
    global _embeddings, _vectorstore, _rag_chain
    if _rag_chain is None:
        print("Loading Knowledge Base (Lazy Loaded)...")
        _embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")
        _vectorstore = FAISS.load_local("vectorstore/faiss_index", _embeddings, allow_dangerous_deserialization=True)
        
        retriever = _vectorstore.as_retriever(search_type="similarity", search_kwargs={"k": 10})
        llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0)

        contextualize_q_prompt = ChatPromptTemplate.from_messages([
            ("system", "Mengingat riwayat obrolan dan pertanyaan terbaru pengguna, formulasikan pertanyaan mandiri. Jangan menjawab, cukup formulasikan ulang jika perlu."),
            MessagesPlaceholder("chat_history"),
            ("human", "{input}"),
        ])
        history_aware_retriever = create_history_aware_retriever(llm, retriever, contextualize_q_prompt)

        system_prompt = """Kamu adalah ASKA (Asisten Akademik Fasilkom UNSIKA). 
TUGAS: Jawab pertanyaan mahasiswa HANYA berdasarkan KONTEKS DOKUMEN yang diberikan.

KONTEKS DOKUMEN:
{context}

PANDUAN EKSEKUSI:
1. DATA DOSEN: Jika ditanya NIDN/Kontak, WAJIB mencari di 'Daftar Dosen Fasilkom Unsika.txt'. Berikan hasil format:
   - **Nama:** [Nama]
   - **NIDN:** [NIDN]
   - **Kontak:** [Nomor]
2. DATA JADWAL: Jika ditanya jadwal, WAJIB mencari di 'Jadwal Kelas Fasilkom Unsika.txt'. Format:
   - **[Hari] (Sesi [Angka])** | Kelas: **[Kelas]** | MK: [MK] | Ruang: [Ruang] | Dosen: [Dosen]
3. UMUM: Gunakan bullet points. Jangan membacakan seluruh dokumen, ambil yang relevan saja.
4. ANTI-HALUSINASI: Jika data benar-benar tidak ada di konteks, jawab: "Maaf, data tidak ditemukan."

PANDUAN PENCARIAN (WAJIB DIIKUTI):
- Kamu bertindak sebagai asisten yang cerdas. Jika mahasiswa bertanya tanpa tanda baca atau gelar (misal: "NIDN Apriade"), kamu WAJIB mengabaikan tanda baca dan gelar tersebut saat mencari di dokumen.
- Fokuslah pada NAMA DEPAN dan NAMA BELAKANG utama.
- Jika nama yang diminta sangat mirip dengan nama di database, ANGGAP ITU ADALAH ORANG YANG SAMA. Jangan katakan data tidak ditemukan jika namanya hanya beda tipis.
"""

        qa_prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            MessagesPlaceholder("chat_history"),
            ("human", "{input}"),
        ])

        _rag_chain = create_retrieval_chain(history_aware_retriever, create_stuff_documents_chain(llm, qa_prompt))
    
    return _rag_chain

# --- FUNGSI LOGGING ---
def simpan_log(pesan_user, jawaban_ai, sumber_list, status="Success", error_msg=""):
    try:
        os.makedirs("logs", exist_ok=True)
        file_path = "logs/chat_logs.csv"
        file_exists = os.path.isfile(file_path)
        
        with open(file_path, mode='a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            if not file_exists:
                writer.writerow(["Waktu", "Pesan User", "Jawaban ASKA", "Sumber Dokumen", "Status", "Error Message"])
            
            waktu_sekarang = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            sumber_teks = " | ".join(sumber_list)
            writer.writerow([waktu_sekarang, pesan_user, jawaban_ai, sumber_teks, status, error_msg])
    except Exception as e:
        print(f"Gagal menulis log: {e}")

# --- ENDPOINT API ---
class Message(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    pesan: str
    history: Optional[List[Message]] = []

@app.post("/chat")
async def chat_endpoint(req: ChatRequest):
    try:
        # Load chain dengan lazy loading
        rag_chain = get_rag_chain()
        
        chat_history = []
        if req.history:
            for msg in req.history[-6:]:
                if msg.role == "user": chat_history.append(HumanMessage(content=msg.content))
                elif msg.role == "assistant": chat_history.append(AIMessage(content=msg.content))

        resp = rag_chain.invoke({
            "input": req.pesan,
            "chat_history": chat_history
        })
        
        jawaban = resp["answer"]
        sumber = list(set([os.path.basename(doc.metadata.get("source", "Dokumen")) for doc in resp.get("context", [])]))
        
        simpan_log(pesan_user=req.pesan, jawaban_ai=jawaban, sumber_list=sumber, status="Success")

        return {"status": "success", "jawaban": jawaban, "sumber": sumber}
    except Exception as e:
        simpan_log(pesan_user=req.pesan, jawaban_ai="", sumber_list=[], status="Error", error_msg=str(e))
        return {"status": "error", "message": str(e)}
