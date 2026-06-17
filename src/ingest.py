import os
os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"
os.environ["OMP_NUM_THREADS"] = "1"
import uuid
from langchain_community.document_loaders import PyMuPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from sentence_transformers import SentenceTransformer
from src.database import supabase

# Load once at import time
embedder = SentenceTransformer("all-MiniLM-L6-v2")


def load_pdf(pdf_path: str):
    """
    Load a PDF file and return a list of Document objects, one per page.
    Each Document has page_content (the text) and metadata (page number, source).
    """
    loader = PyMuPDFLoader(pdf_path)
    documents = loader.load()
    print(f"Loaded {len(documents)} pages from '{pdf_path}'")
    return documents


def chunk_documents(documents: list, chunk_size: int = 500, chunk_overlap: int = 50):
    """
    Split a list of Documents into smaller chunks for retrieval.
    chunk_size: max characters per chunk
    chunk_overlap: characters shared between adjacent chunks (prevents boundary loss)
    """
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
    )
    chunks = splitter.split_documents(documents)
    print(f"Split into {len(chunks)} chunks")
    return chunks


def preview_chunks(chunks: list, n: int = 5):
    """
    Print the first n chunks with their character counts and source page.
    Use this to verify chunking looks correct before moving to embeddings.
    """
    print(f"\n--- First {n} chunks ---\n")
    for i, chunk in enumerate(chunks[:n]):
        char_count = len(chunk.page_content)
        page = chunk.metadata.get("page", "?")
        print(f"Chunk {i+1} | {char_count} chars | page {page}")
        print(chunk.page_content)
        print("-" * 60)


def embed_chunks(chunks: list) -> list[list[float]]:
    """
    Embed a list of Document chunks. Extracts page_content from each
    before encoding, since SentenceTransformer needs raw strings.
    """
    texts = [chunk.page_content for chunk in chunks]
    return embedder.encode(texts, show_progress_bar=True).tolist()


def store_chunks(chunks: list, embeddings: list[list[float]],
                  chatbot_id: str, document_id: str):
    """
    Insert chunks + embeddings into Supabase. Pulls page_content from
    each Document chunk; page number is stashed in case you want it later.
    """
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
    # Insert in batches of 100 to avoid request size limits
    for i in range(0, len(rows), 100):
        supabase.table("chunks").insert(rows[i:i + 100]).execute()
    return len(rows)


def process_document(document_id: str, chatbot_id: str, file_path: str):
    """Called as a background task. Updates document status when done."""
    try:
        documents = load_pdf(file_path)
        chunks = chunk_documents(documents)
        embeddings = embed_chunks(chunks)
        count = store_chunks(chunks, embeddings, chatbot_id, document_id)

        supabase.table("documents").update({
            "status": "ready",
        }).eq("id", document_id).execute()

        print(f"✅ Ingested {count} chunks for document {document_id}")
    except Exception as e:
        supabase.table("documents").update({
            "status": "failed",
            "error_msg": str(e)
        }).eq("id", document_id).execute()
        print(f"❌ Ingestion failed for {document_id}: {e}")


if __name__ == "__main__":
    # Change this to the path of any PDF you have locally
    PDF_PATH = "sample.pdf"

    if not os.path.exists(PDF_PATH):
        print(f"ERROR: '{PDF_PATH}' not found. Put a PDF in your project root and update PDF_PATH.")
    else:
        docs = load_pdf(PDF_PATH)
        chunks = chunk_documents(docs)
        preview_chunks(chunks)