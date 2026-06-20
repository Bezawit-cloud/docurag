import re
import uuid
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from src.auth import get_current_user
from src.database import supabase

router = APIRouter(prefix="/chatbots", tags=["chatbots"])

class ChatbotCreate(BaseModel):
    name: str

def slugify(name: str) -> str:
    base = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
    return f"{base}-{uuid.uuid4().hex[:6]}"

@router.post("", status_code=201)
async def create_chatbot(data: ChatbotCreate, user: dict = Depends(get_current_user)):
    slug = slugify(data.name)
    result = supabase.table("chatbots").insert({
        "user_id": user["id"],
        "name": data.name,
        "slug": slug
    }).execute()

    if not result.data:
        raise HTTPException(400, "Failed to create chatbot")

    return result.data[0]

@router.get("")
async def list_chatbots(user: dict = Depends(get_current_user)):
    result = supabase.table("chatbots").select("*").eq("user_id", user["id"]).execute()
    return result.data