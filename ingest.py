import os
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma

base_dir = os.path.dirname(__file__)
text_path = os.path.join(base_dir, "..", "data", "textbook.txt")
persist_dir = os.path.join(base_dir, "..", "vectordb")

print("📂 Loading text file...")

loader = TextLoader(text_path, encoding="utf-8")
documents = loader.load()

print("✂️ Splitting into chunks...")
text_splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=150)
texts = text_splitter.split_documents(documents)

print(f"📊 Total chunks: {len(texts)}")

print("🧠 Creating embeddings...")
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

print("💾 Storing in ChromaDB...")
vectorstore = Chroma.from_documents(
    documents=texts,
    embedding=embeddings,
    persist_directory=persist_dir
)

vectorstore.persist()

print("✅ DONE! Vector DB ready.")