import os
from dotenv import load_dotenv
from groq import Groq
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")


def load_vectorstore(persist_directory: str = "./chroma_db"):
    """
    Load the existing ChromaDB vector store from disk.
    Must use the same embedding model used during ingestion.
    """
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )
    vectorstore = Chroma(
        persist_directory=persist_directory,
        embedding_function=embeddings
    )
    return vectorstore


def build_retriever(vectorstore, k: int = 4):
    """
    Build a retriever that fetches the top-k most relevant chunks
    for a given query using cosine similarity search.
    """
    retriever = vectorstore.as_retriever(search_kwargs={"k": k})
    return retriever


def build_prompt(question: str, retrieved_chunks: list) -> str:
    """
    Build a prompt that instructs the LLM to answer only from
    the provided context — prevents hallucination.
    """
    context = "\n\n".join([chunk.page_content for chunk in retrieved_chunks])
    prompt = f"""You are a precise document assistant. 
Answer the question using ONLY the context below.
If the answer is not in the context, say "I cannot find this in the document."

Context:
{context}

Question: {question}

Answer:"""
    return prompt


def ask(question: str, retriever, groq_client) -> str:
    """
    Full RAG pipeline:
    1. Retrieve top-k relevant chunks for the question
    2. Build a grounded prompt from those chunks
    3. Send to Groq LLM and return the answer
    """
    retrieved_chunks = retriever.invoke(question)

    print(f"\n--- Retrieved {len(retrieved_chunks)} chunks ---")
    for i, chunk in enumerate(retrieved_chunks):
        page = chunk.metadata.get("page", "?")
        print(f"\nChunk {i+1} (page {page}):")
        print(chunk.page_content[:200], "...")

    prompt = build_prompt(question, retrieved_chunks)

    response = groq_client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2,
    )

    answer = response.choices[0].message.content
    return answer


if __name__ == "__main__":
    print("Loading vector store...")
    vectorstore = load_vectorstore()
    retriever = build_retriever(vectorstore, k=4)
    groq_client = Groq(api_key=GROQ_API_KEY)

    test_question = " what is javafx "

    print(f"\nQuestion: {test_question}")
    answer = ask(test_question, retriever, groq_client)
    print(f"\n--- Answer ---\n{answer}")