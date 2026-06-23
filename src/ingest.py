import os
import uuid
from langchain_community.document_loaders import PyMuPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from sentence_transformers import SentenceTransformer
from src.database import supabase

# Prevent CPU thread explosion (important for local dev)
os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"
os.environ["OMP_NUM_THREADS"] = "1"

# Load embedding model once
embedder = SentenceTransformer("all-MiniLM-L6-v2")


# -----------------------------
# 1. Load PDF
# -----------------------------
def load_pdf(pdf_path: str):
    loader = PyMuPDFLoader(pdf_path)
    documents = loader.load()
    print(f"📄 Loaded {len(documents)} pages from {pdf_path}")
    return documents


# -----------------------------
# 2. Chunk documents
# -----------------------------
def chunk_documents(documents: list, chunk_size: int = 500, chunk_overlap: int = 50):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
    )
    chunks = splitter.split_documents(documents)
    print(f"✂️ Split into {len(chunks)} chunks")
    return chunks


# -----------------------------
# 3. Embed chunks
# -----------------------------
def embed_chunks(chunks: list) -> list[list[float]]:
    texts = [chunk.page_content for chunk in chunks]
    embeddings = embedder.encode(texts, show_progress_bar=True)
    return embeddings.tolist()


# -----------------------------
# 4. Store in Supabase
# -----------------------------
def store_chunks(chunks: list, embeddings: list[list[float]],
                 chatbot_id: str, document_id: str):

    rows = [
        {
            "id": str(uuid.uuid4()),
            "chatbot_id": chatbot_id,
            "document_id": document_id,
            "content": chunk.page_content,
            "embedding": embedding,
        }
        for chunk, embedding in zip(chunks, embeddings)
    ]

    # batch insert (safe for Supabase limits)
    for i in range(0, len(rows), 100):
        supabase.table("chunks").insert(rows[i:i + 100]).execute()

    return len(rows)


# -----------------------------
# 5. Main ingestion pipeline
# -----------------------------
def process_document(document_id: str, chatbot_id: str, file_path: str):
    try:
        print("🚀 Starting ingestion pipeline...")

        # Step 1: Load PDF
        documents = load_pdf(file_path)

        # Step 2: Chunk text
        chunks = chunk_documents(documents)

        if not chunks:
            raise ValueError("No chunks generated from PDF")

        # Step 3: Create embeddings
        embeddings = embed_chunks(chunks)

        # Step 4: Store in DB
        count = store_chunks(chunks, embeddings, chatbot_id, document_id)

        # Step 5: Update document status (SUCCESS)
        supabase.table("documents").update({
            "status": "ready",
            "chunk_count": count,
            "error_msg": None
        }).eq("id", document_id).execute()

        print(f"✅ Successfully processed {count} chunks for document {document_id}")

    except Exception as e:
        # Always safe fallback (no undefined variables)
        print(f"❌ Ingestion failed: {str(e)}")

        supabase.table("documents").update({
            "status": "failed",
            "chunk_count": 0,
            "error_msg": str(e)
        }).eq("id", document_id).execute()


# -----------------------------
# 6. Local test runner
# -----------------------------
if __name__ == "__main__":
    PDF_PATH = "sample.pdf"

    if not os.path.exists(PDF_PATH):
        print("❌ PDF not found. Add sample.pdf to test.")
    else:
        docs = load_pdf(PDF_PATH)
        chunks = chunk_documents(docs)
        print(f"Preview chunks: {len(chunks)}")