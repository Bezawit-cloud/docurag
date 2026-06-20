from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr
from src.database import supabase

router = APIRouter(prefix="/auth", tags=["auth"])

class SignupRequest(BaseModel):
    email: EmailStr
    password: str

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

@router.post("/signup", status_code=201)
async def signup(data: SignupRequest):
    try:
        result = supabase.auth.sign_up({
            "email": data.email,
            "password": data.password
        })
        if result.user is None:
            raise HTTPException(400, "Signup failed")

        # Create a matching profile row for plan tracking
        supabase.table("user_profiles").insert({
            "id": result.user.id,
            "plan": "free"
        }).execute()

        return {
            "user_id": result.user.id,
            "email": result.user.email,
            "access_token": result.session.access_token if result.session else None,
            "message": "Signup successful. Check email for confirmation if required."
        }
    except Exception as e:
        raise HTTPException(400, f"Signup failed: {str(e)}")

@router.post("/login")
async def login(data: LoginRequest):
    try:
        result = supabase.auth.sign_in_with_password({
            "email": data.email,
            "password": data.password
        })
        if result.session is None:
            raise HTTPException(401, "Invalid credentials")

        return {
            "access_token": result.session.access_token,
            "refresh_token": result.session.refresh_token,
            "user_id": result.user.id,
            "email": result.user.email
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(401, f"Login failed: {str(e)}")