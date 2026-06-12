# UI-upgraded version generated for ASKA
import streamlit as st
import os
import json
import random
from datetime import datetime
from dotenv import load_dotenv
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_classic.chains import create_history_aware_retriever, create_retrieval_chain
from langchain_classic.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage

# ─────────────────────────────────────────────
# 1. PAGE CONFIG & ASSETS
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="ASKA - Chatbot Akademik",
    page_icon="🎓",
    layout="centered",
    initial_sidebar_state="expanded"
)

logo_path = "Asisten Akademik Fasilkom Unsika.png"
if not os.path.exists(logo_path):
    logo_path = None

# ─────────────────────────────────────────────
# 2. ULTRA-CUSTOM CSS (Meniru Tailwind Mockup)
# ─────────────────────────────────────────────
st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
<link href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:opsz,wght,FILL,GRAD@24,400,1,0" rel="stylesheet">
<style>
/* Reset & Base Font */
html, body, [class*="css"] { font-family: 'Inter', sans-serif !important; }
#MainMenu, header, footer { visibility: hidden !important; }

/* Background Utama */
.stApp { background-color: #fcfcfd !important; }
[data-testid="stMainBlockContainer"] { max-width: 800px; padding-top: 3rem !important; padding-bottom: 8rem !important; }

/* ── SIDEBAR ── */
[data-testid="stSidebar"] {
    background-color: #f4f6f8 !important;
    border-right: 1px solid #e0e3e8 !important;
}
.sb-header { display: flex; align-items: center; gap: 12px; margin-bottom: 24px; }
.sb-avatar { width: 40px; height: 40px; background: #ffffff; border-radius: 50%; display: flex; justify-content: center; align-items: center; border: 1px solid #e0e3e8; color: #8A1538; }
.sb-title { font-weight: 700; font-size: 1.1rem; color: #181c20; margin: 0; line-height: 1.2; }
.sb-status { font-size: 0.75rem; color: #626566; display: flex; align-items: center; gap: 6px; margin-top: 2px;}
.sb-status-dot { width: 6px; height: 6px; background-color: #22c55e; border-radius: 50%; }

/* Sidebar Buttons Specific Rules */
[data-testid="stSidebar"] [data-testid="stHorizontalBlock"] [data-testid="column"]:nth-child(1) button {
    background-color: #8A1538 !important;
    color: white !important;
    border: none !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
}
[data-testid="stSidebar"] [data-testid="stHorizontalBlock"] [data-testid="column"]:nth-child(2) button {
    background-color: transparent !important;
    color: #181c20 !important;
    border: 1px solid #e0e3e8 !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
}

/* Sidebar Sections */
.sb-label { font-size: 0.7rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.05em; color: #626566; margin: 28px 0 12px 0; display: flex; align-items: center; gap: 8px; }
.sb-item { display: flex; align-items: center; gap: 12px; padding: 10px 0; color: #454748; font-size: 0.85rem; cursor: pointer; }
.sb-item span.icon { font-size: 18px; }

/* ── MAIN CHAT AREA ── */
.hero-box { text-align: center; margin-top: 2rem; margin-bottom: 2rem; }
.hero-title { font-size: 1.75rem; font-weight: 700; color: #181c20; margin-top: 12px; margin-bottom: 8px; }
.hero-subtitle { font-size: 0.95rem; color: #626566; max-width: 550px; margin: 0 auto; line-height: 1.5; }

/* Suggestion Pills */
.suggest-pill { display: flex; justify-content: center; }
.suggest-pill button {
    background-color: #f1f4f9 !important;
    border: 1px solid #e0e3e8 !important;
    color: #181c20 !important;
    border-radius: 999px !important;
    padding: 6px 16px !important;
    font-size: 0.85rem !important;
    transition: all 0.2s;
    min-height: 0 !important;
    height: auto !important;
}
.suggest-pill button:hover { background-color: #e0e3e8 !important; }

/* ── CHAT BUBBLES ASIMETRIS ── */
[data-testid="stChatMessage"] { background: transparent !important; margin-bottom: 1rem !important; padding: 0 !important; }

/* User Bubble (Kanan, Sudut Kanan Atas Tajam) */
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) { flex-direction: row-reverse !important; }
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) .stMarkdown {
    background-color: #8A1538 !important;
    color: white !important;
    border-radius: 16px 4px 16px 16px !important; /* Sesuai mockup tailwind */
    padding: 12px 18px !important;
    max-width: 80% !important;
    font-size: 0.95rem !important;
}
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) [data-testid="chatAvatarIcon-user"] { display: none !important; }

/* Bot Bubble (Kiri, Sudut Kiri Atas Tajam) */
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"]) { flex-direction: row !important; }
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"]) .stMarkdown {
    background-color: #f1f4f9 !important;
    color: #181c20 !important;
    border-radius: 4px 16px 16px 16px !important; /* Sesuai mockup tailwind */
    padding: 14px 20px !important;
    max-width: 85% !important;
    font-size: 0.95rem !important;
    border: none !important;
}
[data-testid="chatAvatarIcon-assistant"] { border: 1px solid #e0e3e8 !important; background-color: white !important; border-radius: 50% !important;}

/* ── CHAT INPUT (Floating & Disclaimer) ── */
[data-testid="stBottomBlockContainer"] { 
    background: linear-gradient(to top, #fcfcfd 85%, transparent) !important; 
    padding-bottom: 1.5rem !important;
}
[data-testid="stChatInput"] {
    border-radius: 24px !important;
    border: 1px solid #e0e3e8 !important;
    background-color: #ffffff !important;
    box-shadow: 0 4px 12px rgba(0,0,0,0.03) !important;
}
[data-testid="stChatInput"]:focus-within { border-color: #8A1538 !important; }
[data-testid="stChatInput"] textarea { padding: 12px 16px !important; color: #181c20 !important; }
[data-testid="stChatInput"] button {
    background-color: #8A1538 !important;
    color: white !important;
    border-radius: 50% !important;
    width: 32px !important;
    height: 32px !important;
    margin: 4px !important;
}

/* Disclaimer Text via CSS Pseudo-element */
[data-testid="stBottomBlockContainer"]::after {
    content: "ASKA dapat membuat kesalahan. Harap verifikasi informasi penting dengan pihak fakultas.";
    display: block;
    text-align: center;
    font-size: 10px;
    color: #8c8f91;
    margin-top: 10px;
    font-family: 'Inter', sans-serif;
}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# 3. KNOWLEDGE BASE & LOGIC
# ─────────────────────────────────────────────
QUESTIONS_BY_TOPIC = {
    "kalender": ["Kapan batas KRS semester ini?"],
    "magang": ["Syarat daftar magang?"],
    "jadwal": ["Jadwal kelas Pemrograman Web?"]
}
ALL_QUESTIONS = [q for qs in QUESTIONS_BY_TOPIC.values() for q in qs]

@st.cache_resource
def load_knowledge_base():
    load_dotenv()
    if not os.getenv("GEMINI_API_KEY") or not os.path.exists("vectorstore/faiss_index"):
        st.error("API Key hilang atau Vectorstore belum ada.")
        st.stop()
    
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")
    vectorstore = FAISS.load_local("vectorstore/faiss_index", embeddings, allow_dangerous_deserialization=True)
    retriever = vectorstore.as_retriever(search_type="similarity", search_kwargs={"k": 20})
    llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0)

    ctx_prompt = ChatPromptTemplate.from_messages([
        ("system", "Formulasikan pertanyaan mandiri dari history."),
        MessagesPlaceholder("chat_history"), ("human", "{input}")
    ])
    qa_prompt = ChatPromptTemplate.from_messages([
        ("system", "Kamu adalah ASKA, Asisten Akademik resmi Fasilkom UNSIKA. Jawab HANYA berdasar konteks:\n\n{context}"),
        MessagesPlaceholder("chat_history"), ("human", "{input}")
    ])
    return create_retrieval_chain(create_history_aware_retriever(llm, retriever, ctx_prompt), create_stuff_documents_chain(llm, qa_prompt))

rag_chain = load_knowledge_base()

CHAT_DIR = "chat_history"
os.makedirs(CHAT_DIR, exist_ok=True)
def save_chat(chat_id, msgs):
    with open(os.path.join(CHAT_DIR, f"{chat_id}.json"), "w") as f: json.dump(msgs, f)
def load_chat(chat_id):
    if os.path.exists(p:=os.path.join(CHAT_DIR, f"{chat_id}.json")): return json.load(open(p))
    return []
def get_all_chats():
    chats = []
    for fn in sorted(os.listdir(CHAT_DIR), reverse=True):
        if fn.endswith(".json"):
            data = json.load(open(os.path.join(CHAT_DIR, fn)))
            if data: chats.append({"id": fn[:-5], "preview": data[0]["content"][:30]})
    return chats

if "messages" not in st.session_state: st.session_state.messages = []
if "chat_id" not in st.session_state: st.session_state.chat_id = None
if "pending_q" not in st.session_state: st.session_state.pending_q = None

# ─────────────────────────────────────────────
# 4. SIDEBAR
# ─────────────────────────────────────────────
with st.sidebar:
    # Header Identity
    st.markdown("""
        <div class="sb-header">
            <div class="sb-avatar"><span class="material-symbols-outlined" style="font-size: 20px;">school</span></div>
            <div>
                <div class="sb-title">Chatbot Akademik</div>
                <div class="sb-status"><div class="sb-status-dot"></div> Online</div>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    # Action Buttons
    c1, c2 = st.columns(2)
    with c1:
        if st.button("➕ Chat Baru", use_container_width=True):
            st.session_state.chat_id = datetime.now().strftime("%Y%m%d_%H%M%S")
            st.session_state.messages = []
            st.rerun()
    with c2:
        if st.button("🗑️ Hapus", use_container_width=True):
            if st.session_state.chat_id and os.path.exists(f"{CHAT_DIR}/{st.session_state.chat_id}.json"):
                os.remove(f"{CHAT_DIR}/{st.session_state.chat_id}.json")
            st.session_state.messages = []
            st.session_state.chat_id = None
            st.rerun()

    # Documents Section
    st.markdown('<div class="sb-label"><span class="material-symbols-outlined" style="font-size:16px;">push_pin</span> DOKUMEN TERSEDIA</div>', unsafe_allow_html=True)
    st.markdown("""
        <div class="sb-item"><span class="material-symbols-outlined icon" style="color:#8A1538;">calendar_month</span> Kalender Akademik</div>
        <div class="sb-item"><span class="material-symbols-outlined icon" style="color:#3b82f6;">work</span> Panduan Magang</div>
        <div class="sb-item"><span class="material-symbols-outlined icon" style="color:#ef4444;">description</span> Panduan Tugas Akhir</div>
        <div class="sb-item"><span class="material-symbols-outlined icon" style="color:#eab308;">group</span> Daftar Dosen</div>
        <div class="sb-item"><span class="material-symbols-outlined icon" style="color:#6366f1;">schedule</span> Jadwal Kelas</div>
    """, unsafe_allow_html=True)

    # History Section
    st.markdown('<div class="sb-label"><span class="material-symbols-outlined" style="font-size:16px;">history</span> RIWAYAT CHAT</div>', unsafe_allow_html=True)
    chats = get_all_chats()
    if not chats:
        st.markdown('<div style="font-size:0.8rem; color:#8c8f91; font-style:italic; padding-top:8px;">Belum ada riwayat chat.</div>', unsafe_allow_html=True)
    else:
        for c in chats:
            if st.button(f"📄 {c['preview']}...", key=f"h_{c['id']}", use_container_width=True):
                st.session_state.chat_id = c["id"]
                st.session_state.messages = load_chat(c["id"])
                st.rerun()

# ─────────────────────────────────────────────
# 5. MAIN CHAT AREA
# ─────────────────────────────────────────────
chat_container = st.container()

with chat_container:
    if not st.session_state.messages:
        # Hero Section
        st.markdown('<div class="hero-box">', unsafe_allow_html=True)
        if logo_path:
            st.image(logo_path, width=100)
        st.markdown('<div class="hero-title">Halo, Mahasiswa!</div>', unsafe_allow_html=True)
        st.markdown('<div class="hero-subtitle">Saya ASKA, Asisten Akademik Fasilkom Unsika. Siap membantu Anda dengan informasi akademik dari dokumen terlampir.</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Suggestion Pills (Wrapped in CSS columns for perfect centering)
        st.write("")
        c1, c2, c3, c4, c5 = st.columns([1, 3, 3, 3, 1]) # Flexbox hack for Streamlit
        cols_center = [c2, c3, c4]
        for i, q in enumerate(ALL_QUESTIONS[:3]):
            with cols_center[i]:
                st.markdown('<div class="suggest-pill">', unsafe_allow_html=True)
                if st.button(q, key=f"sug_{i}", use_container_width=True):
                    st.session_state.pending_q = q
                    st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)
    else:
        # Chat Rendering
        for msg in st.session_state.messages:
            ava = logo_path if msg["role"] == "assistant" and logo_path else "👤"
            with st.chat_message(msg["role"], avatar=ava):
                st.markdown(msg["content"])
                if msg.get("sources"):
                    with st.expander("📚 Lihat Sumber"):
                        for s in msg["sources"]: st.markdown(s)

# ─────────────────────────────────────────────
# 6. INPUT & RAG EXECUTION
# ─────────────────────────────────────────────
user_input = st.chat_input("Tanya apa pun tentang akademik Fasilkom...")
if st.session_state.pending_q:
    user_input = st.session_state.pending_q
    st.session_state.pending_q = None

if user_input:
    if not st.session_state.chat_id: st.session_state.chat_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    st.session_state.messages.append({"role": "user", "content": user_input})
    save_chat(st.session_state.chat_id, st.session_state.messages)
    
    with chat_container:
        with st.chat_message("user"): st.markdown(user_input)
        with st.chat_message("assistant", avatar=logo_path):
            with st.spinner("Mencari..."):
                hist = [HumanMessage(content=m["content"]) if m["role"]=="user" else AIMessage(content=m["content"]) for m in st.session_state.messages[:-1]]
                try:
                    resp = rag_chain.invoke({"input": user_input, "chat_history": hist})
                    st.markdown(resp["answer"])
                    citations = list({f"- **{os.path.basename(d.metadata.get('source',''))}**\n> *\"{d.page_content[:80]}...\"*" for d in resp.get("context",[])})
                    if citations:
                        with st.expander("📚 Lihat Sumber"):
                            for c in citations: st.markdown(c)
                    st.session_state.messages.append({"role": "assistant", "content": resp["answer"], "sources": citations})
                    save_chat(st.session_state.chat_id, st.session_state.messages)
                except Exception as e:
                    st.error(f"Error: {e}")