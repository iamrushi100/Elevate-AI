print("RAG FILE EXECUTING...")

import os
from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

# Path to vectordb
base_dir = os.path.dirname(__file__)
persist_dir = os.path.join(base_dir, "..", "vectordb")

# Load embeddings (same as ingest.py)
embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

# Load existing vector DB
vectordb = Chroma(
    persist_directory=persist_dir,
    embedding_function=embeddings
)

# Return retriever
def get_retriever():
    return vectordb.as_retriever(search_kwargs={"k": 3})