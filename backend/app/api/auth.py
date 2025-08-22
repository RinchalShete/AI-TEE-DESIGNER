from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel, EmailStr
from app.utils.security import hash_password, verify_password, create_access_token, decode_access_token
from app.supabase_client import supabase

router = APIRouter(prefix="/auth", tags=["auth"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


# Pydantic models for request bodies
class SignupRequest(BaseModel):
    username: str
    email: EmailStr
    password: str

class LoginRequest(BaseModel):
    email: EmailStr
    password: str


# Dependency to get current user from token
async def get_current_user(token: str = Depends(oauth2_scheme)):
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )
    return payload


@router.post("/signup")
async def signup(data: SignupRequest):
    # Check if user with email or username exists
    user_check = supabase.table("users") \
        .select("*") \
        .or_(f"email.eq.{data.email},username.eq.{data.username}") \
        .execute()

    if user_check.data and len(user_check.data) > 0:
        raise HTTPException(status_code=400, detail="User with this email or username already exists")

    # Hash password
    hashed_password = hash_password(data.password)

    # Insert user into Supabase
    response = supabase.table("users").insert({
        "username": data.username,
        "email": data.email,
        "password_hash": hashed_password
    }).execute()

    if getattr(response, "error", None):
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create user: {response.error}"
        )

    if not response.data:
        raise HTTPException(
            status_code=500,
            detail="User creation failed: no data returned from Supabase"
        )

    # Auto-login after signup: create JWT token
    user = response.data[0]
    token = create_access_token({"sub": user["id"], "username": user["username"]})

    return {
        "message": "User created successfully and logged in",
        "user": user,
        "access_token": token,
        "token_type": "bearer"
    }


@router.post("/login")
async def login(data: LoginRequest):
    # Find user by email
    response = supabase.table("users").select("*").eq("email", data.email).execute()

    user = response.data[0] if response.data else None
    if not user:
        raise HTTPException(status_code=400, detail="Invalid credentials")

    # Verify password
    if not verify_password(data.password, user["password_hash"]):
        raise HTTPException(status_code=400, detail="Invalid credentials")

    # Create JWT token
    token = create_access_token({"sub": user["id"], "username": user["username"]})

    return {"access_token": token, "token_type": "bearer"}


@router.get("/me")
async def get_me(current_user: dict = Depends(get_current_user)):
    # Just return whatever payload was in the token
    return {"sub": current_user["sub"], "username": current_user["username"]}
