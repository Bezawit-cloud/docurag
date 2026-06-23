import os
import shutil
import uuid
from fastapi import APIRouter, UploadFile, File, Form, BackgroundTasks, Depends, HTTPException
from src.auth import get_current_user
from src.ingest import process_document
from src.database import supabase

router = APIRouter(prefix="/documents", tags=["documents"])

ALLOWED_EXTENSIONS = [".pdf", ".docx", ".txt"]

@router.post("/upload", status_code=202)
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    chatbot_id: str = Form(...),
    user: dict = Depends(get_current_user)
):
    # Validate file type
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(415, f"Unsupported type. Allowed: {ALLOWED_EXTENSIONS}")

    # Confirm the chatbot belongs to this user
    chatbot = supabase.table("chatbots").select("id").eq("id", chatbot_id).eq("user_id", user["id"]).execute()
    if not chatbot.data:
        raise HTTPException(404, "Chatbot not found or not yours")

    
    # Save to temp location
    doc_id = str(uuid.uuid4())
    os.makedirs("uploads", exist_ok=True)
    tmp_path = f"uploads/{doc_id}{ext}"
    with open(tmp_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    # Insert document record
    supabase.table("documents").insert({
        "id": doc_id,
        "chatbot_id": chatbot_id,
        "filename": file.filename,
        "storage_path": tmp_path,
        "status": "processing"
    }).execute()

    # Kick off background processing
    background_tasks.add_task(process_document, doc_id, chatbot_id, tmp_path)

    return {
        "document_id": doc_id,
        "status": "processing",
        "poll_url": f"/documents/{doc_id}/status"
    }

@router.get("/{document_id}/status")
async def get_status(document_id: str, user: dict = Depends(get_current_user)):
    result = supabase.table("documents").select(
        "id, status, chunk_count, error_msg, filename"
    ).eq("id", document_id).execute()

    if not result.data:
        raise HTTPException(404, "Document not found")

    return result.data[0]