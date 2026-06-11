# DocuRAG — PDF Question Answering System

## What it does
Turns any PDF into an interactive AI assistant using RAG 
(Retrieval-Augmented Generation). Ask questions in plain English, 
get grounded answers with page citations.

## How it works
1. Load PDF → extract text
2. Split into 500-character chunks
3. Convert chunks to embedding vectors
4. Store vectors in ChromaDB
5. On question: retrieve top-k relevant chunks
6. Send chunks + question to Groq LLM
7. Return grounded answer

## How to run
```bash
git clone https://github.com/Bezawit-cloud/docurag
cd docurag
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
# Add your GROQ_API_KEY to .env
python main.py
```

## What I learned about chunking
- chunk_size=300: precise retrieval but loses cross-sentence context
- chunk_size=500: best balance of precision and context
- chunk_size=800: more context but retrieval becomes noisy
- overlap=50: critical for preserving meaning at chunk boundaries

## What I learned about retrieval
- k=3: strict, accurate, but misses scattered information
- k=4: best balance for most document types
- k=6: more complete but introduces irrelevant context

## Key insight
RAG quality depends more on chunking strategy and prompt 
engineering than on the LLM itself.

## Tech stack
- Python, LangChain, ChromaDB
- HuggingFace sentence-transformers
- Groq LLM (llama-3.1-8b-instant)