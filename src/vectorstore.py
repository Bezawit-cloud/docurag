from ingest import load_pdf, chunk_documents

from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma

PDF_PATH = "sample.pdf"

# Load PDF
docs = load_pdf(PDF_PATH)

# Create chunks
chunks = chunk_documents(docs)

# Create embedding model
embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

# Create vector database
vectorstore = Chroma(
    persist_directory="./chroma_db",
    embedding_function=embeddings
)

# Store chunks
vectorstore.add_documents(chunks)

# Verify storage
print(f"Stored {vectorstore._collection.count()} chunks")