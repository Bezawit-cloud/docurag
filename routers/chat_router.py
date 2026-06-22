from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from src.database import supabase
from src.retrieval import search
from src.llm import generate_answer

router = APIRouter(prefix="/chat", tags=["chat"])

class ChatRequest(BaseModel):
    question: str

@router.post("/{slug}")
async def chat(slug: str, data: ChatRequest):
    if not data.question or not data.question.strip():
        raise HTTPException(400, "Question cannot be empty")

    # Look up chatbot by public slug
    chatbot = supabase.table("chatbots").select("id, name").eq("slug", slug).execute()
    if not chatbot.data:
        raise HTTPException(404, f"No chatbot found with slug '{slug}'")

    chatbot_id = chatbot.data[0]["id"]

    # Retrieve relevant chunks
    chunks = search(data.question, chatbot_id, k=4)

    if not chunks:
        return {
            "answer": "I don't have any documents to search yet for this chatbot.",
            "sources": []
        }

    # Pass the question and the raw chunks list directly to the LLM function
    answer = generate_answer(data.question, chunks)

    return {
        "answer": answer,
        "sources": [
            {"content": c["content"][:200], "similarity": round(c["similarity"], 3)}
            for c in chunks
        ]
    }