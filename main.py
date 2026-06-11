import os
import time
from dotenv import load_dotenv
from groq import Groq
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_community.document_loaders import PyMuPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

load_dotenv()


def build_pipeline(pdf_path: str, chunk_size: int = 500, chunk_overlap: int = 50, k: int = 4):
    """
    Full RAG pipeline:
    Load PDF → Chunk → Embed → Store → Return retriever + Groq client
    """

    print(f"\nLoading '{pdf_path}'...")
    loader = PyMuPDFLoader(pdf_path)
    documents = loader.load()

    print(f"Loaded {len(documents)} pages")

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap
    )
    chunks = splitter.split_documents(documents)

    print(f"Split into {len(chunks)} chunks (size={chunk_size}, overlap={chunk_overlap})")

    # ---------------- EMBEDDING ----------------
    print("\nEmbedding stage starting (this may take 1–3 minutes)...")

    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

    texts = []
    metadatas = []

    for i, chunk in enumerate(chunks):
        print(f"Embedding chunk {i+1}/{len(chunks)}")
        texts.append(chunk.page_content)
        metadatas.append(chunk.metadata)

    vectorstore = Chroma.from_texts(
        texts=texts,
        embedding=embeddings,
        metadatas=metadatas,
        persist_directory="./chroma_db"
    )

    print("\nEmbedding complete ✔")

    retriever = vectorstore.as_retriever(search_kwargs={"k": k})

    groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))

    print(f"Pipeline ready ✔ (top {k} chunks retrieval enabled)\n")

    return retriever, groq_client


def ask(question: str, retriever, groq_client) -> str:
    """
    Retrieve context + generate grounded answer using Groq
    """

    chunks = retriever.invoke(question)

    context = "\n\n".join([c.page_content for c in chunks])

    prompt = f"""You are a precise document assistant.

Answer ONLY using the context below.
If the answer is not in the context, say:
"I cannot find this in the document."

Context:
{context}

Question: {question}

Answer clearly and mention where the information comes from if possible.
"""

    response = groq_client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2,
    )

    time.sleep(1)

    return response.choices[0].message.content


def query_loop(retriever, groq_client):
    """
    Interactive chat loop
    """

    print("=" * 50)
    print("DocuRAG is ready 🚀 Ask anything about your PDF")
    print("Type 'exit' to quit")
    print("=" * 50)

    while True:
        question = input("\nYou: ").strip()

        if question.lower() in ["exit", "quit", ""]:
            print("Exiting...")
            break

        answer = ask(question, retriever, groq_client)

        print(f"\nAnswer:\n{answer}")
        print("-" * 50)


if __name__ == "__main__":

    PDF_PATH = "medical.pdf"

    if not os.path.exists(PDF_PATH):
        print(f"ERROR: '{PDF_PATH}' not found.")
    else:
        try:
            retriever, groq_client = build_pipeline(PDF_PATH)
            query_loop(retriever, groq_client)

        except Exception as e:
            print(f"\nERROR OCCURRED: {e}")