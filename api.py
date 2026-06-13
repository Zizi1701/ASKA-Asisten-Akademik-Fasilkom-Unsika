import os
import csv
from datetime import datetime
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
# Menggunakan model yang lebih ringan agar tidak crash di RAM Render
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
vectorstore = FAISS.load_local("vectorstore/faiss_index", embeddings, allow_dangerous_deserialization=True)
llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0)

# Mengatur retriever dengan k=3 agar respons lebih cepat & ringan
retriever = vectorstore.as_retriever(search_type="similarity", search_kwargs={"k": 3})

contextualize_q_prompt = ChatPromptTemplate.from_messages([
    ("system", "Formulasikan ulang pertanyaan menjadi pertanyaan mandiri."),
    MessagesPlaceholder("chat_history"),
    ("human", "{input}"),
])
history_aware_retriever = create_history_aware_retriever(llm, retriever, contextualize_q_prompt)

system_prompt = """Kamu adalah ASKA (Asisten Akademik Fasilkom UNSIKA). 
Jawab hanya berdasarkan konteks dokumen yang diberikan. Jika tidak ada, jawab: "Maaf, data tidak ditemukan."
KONTEKS: {context}"""

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

@app.get("/", include_in_schema=False)
async def read_index():
    return FileResponse("index.html")

@app.get("/logo-aska.png")
async def get_image():
    return FileResponse("logo-aska.png")

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

        # Menjalankan chain yang sudah di-load di awal
        resp = rag_chain.invoke({"input": req.pesan, "chat_history": chat_history})
        
        jawaban = resp["answer"]
        sumber = list(set([os.path.basename(doc.metadata.get("source", "Dokumen")) for doc in resp.get("context", [])]))
        
        return {"status": "success", "jawaban": jawaban, "sumber": sumber}
    except Exception as e:
        return {"status": "error", "message": str(e)}