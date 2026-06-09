import os
from langchain_community.document_loaders import PyMuPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter


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


if __name__ == "__main__":
    # Change this to the path of any PDF you have locally
    PDF_PATH = "sample.pdf"

    if not os.path.exists(PDF_PATH):
        print(f"ERROR: '{PDF_PATH}' not found. Put a PDF in your project root and update PDF_PATH.")
    else:
        docs = load_pdf(PDF_PATH)
        chunks = chunk_documents(docs)
        preview_chunks(chunks)