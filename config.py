# Central config — change values here, affects entire pipeline
CHUNK_SIZE = 500
CHUNK_OVERLAP = 50
RETRIEVAL_K = 4
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
GROQ_MODEL = "llama-3.1-8b-instant"
PERSIST_DIR = "./chroma_db"