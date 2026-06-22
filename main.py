from fastapi import FastAPI, Depends
from routers import auth_router, chatbot_router, document_router, chat_router
from src.auth import get_current_user

app = FastAPI(title="DocuRAG API")

app.include_router(auth_router.router)
app.include_router(chatbot_router.router)
app.include_router(document_router.router)
app.include_router(chat_router.router)

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.get("/me")
async def read_me(user: dict = Depends(get_current_user)):
    return {"authenticated_as": user}