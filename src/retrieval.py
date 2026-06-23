from sentence_transformers import SentenceTransformer
from src.database import supabase

# Initialize model once
embedder = SentenceTransformer("all-MiniLM-L6-v2")

def search(question: str, chatbot_id: str, k: int = 4) -> list[dict]:
    # 1. Convert query to vector
    question_embedding = embedder.encode(question).tolist()

    # 2. Call the RPC with explicit parameters
    # Adding match_threshold=0.0 ensures we get results for testing
    result = supabase.rpc("match_chunks", {
        "query_embedding": question_embedding,
        "match_chatbot_id": chatbot_id,
        "match_count": k,
        "match_threshold": 0.0 
    }).execute()

    # 3. Debugging: Print count to terminal to confirm database is returning data
    print(f"DEBUG: Found {len(result.data)} chunks for chatbot {chatbot_id}")
    
    return result.data