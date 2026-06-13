import os
from langchain_community.document_loaders import TextLoader
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_text_splitters import CharacterTextSplitter

# 1. Konfigurasi
MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
DOCS_DIR = "./data"  # Pastikan folder ini berisi file .txt Anda
INDEX_DIR = "vectorstore/faiss_index"

# 2. Load Dokumen
print("Loading documents...")
documents = []
for filename in os.listdir(DOCS_DIR):
    if filename.endswith(".txt"):
        loader = TextLoader(os.path.join(DOCS_DIR, filename), encoding='utf-8')
        documents.extend(loader.load())

# 3. Split Dokumen
text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
texts = text_splitter.split_documents(documents)

# 4. Generate Embeddings & Save Index
print(f"Generating embeddings using {MODEL_NAME}...")
embeddings = HuggingFaceEmbeddings(model_name=MODEL_NAME)
vectorstore = FAISS.from_documents(texts, embeddings)

print(f"Saving index to {INDEX_DIR}...")
os.makedirs("vectorstore", exist_ok=True)
vectorstore.save_local(INDEX_DIR)
print("Done!")