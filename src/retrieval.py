from sentence_transformers import SentenceTransformer
from src.database import supabase

embedder = SentenceTransformer("all-MiniLM-L6-v2")

def search(question: str, chatbot_id: str, k: int = 4) -> list[dict]:
    question_embedding = embedder.encode(question).tolist()

    result = supabase.rpc("match_chunks", {
        "query_embedding": question_embedding,
        "match_chatbot_id": chatbot_id,
        "match_count": k
    }).execute()

    return result.data  # list of {id, content, similarity}