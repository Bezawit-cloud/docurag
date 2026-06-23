# tests/test_ingest.py
import os
os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"

from src.database import supabase
from src.ingest import load_pdf, chunk_documents, embed_chunks, store_chunks
from src.retrieval import search

# You'll need a real chatbot row for the FK constraint.
TEST_CHATBOT_ID = "f2beba78-9449-4495-bd55-fd327dce3028"
TEST_PDF = "sample.pdf"


def test_full_ingest_and_search():
    # 1. Prepare the document
    TEST_DOC_ID = str(uuid.uuid4())
    
    # Register the document in the 'documents' table first
    supabase.table("documents").insert({
        "id": TEST_DOC_ID,
        "chatbot_id": TEST_CHATBOT_ID,
        "filename": "test_pdf.pdf",
        "status": "processing"
    }).execute()

    # 2. Ingest
    documents = load_pdf(TEST_PDF)
    chunks = chunk_documents(documents)
    embeddings = embed_chunks(chunks)

    # 3. Store chunks using the ID you just registered
    count = store_chunks(chunks, embeddings, TEST_CHATBOT_ID, TEST_DOC_ID)
    print(f"Stored {count} chunks for document {TEST_DOC_ID}")
    assert count > 0



    # Search
    results = search("what is this document about?", TEST_CHATBOT_ID)
    print(f"Top result: {results[0]['content'][:200]}")
    assert len(results) > 0
    assert results[0]['similarity'] > 0


if __name__ == "__main__":
    test_full_ingest_and_search()
    print("✅ All good — pgvector is working!")
    