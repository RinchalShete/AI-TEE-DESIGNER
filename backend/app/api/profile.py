from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime, timedelta
import random, string
import os
import smtplib
from email.mime.text import MIMEText
from dotenv import load_dotenv

from app.supabase_client import supabase
from app.utils.security import hash_password, decode_access_token

# ---------------- Load .env ----------------
load_dotenv()
SMTP_SERVER = os.getenv("SMTP_SERVER")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
SMTP_EMAIL = os.getenv("SMTP_EMAIL")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")

# ---------------- Router ----------------
router = APIRouter(prefix="/profile", tags=["Profile"])

# ---------------- OTP Cache ----------------
otp_cache = {}

# ---------------- Models ----------------
class UpdateProfileRequest(BaseModel):
    username: Optional[str] = None

class ForgotPasswordRequest(BaseModel):
    email: EmailStr

class VerifyOtpRequest(BaseModel):
    email: EmailStr
    otp: str

class NewPasswordRequest(BaseModel):
    email: EmailStr
    new_password: str

# ---------------- OAuth2 Scheme ----------------
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

# ---------------- Email Utils ----------------
def send_email(to_email: str, subject: str, otp: str):
    body = f"""
    <html>
      <body style="font-family: Arial, sans-serif; background-color: #f6f6f6; padding: 20px;">
        <div style="max-width: 500px; margin: auto; background: #ffffff; padding: 30px; border-radius: 10px; box-shadow: 0px 4px 10px rgba(0,0,0,0.1);">
          <h2 style="color: #333333; text-align: center;">Password Reset Request</h2>
          <p>Hi there,</p>
          <p>We received a request to reset your password. Use the OTP below to proceed:</p>
          <p style="text-align: center; font-size: 24px; font-weight: bold; color: #1a73e8; margin: 20px 0;">{otp}</p>
          <p>This OTP is valid for <b>5 minutes</b>. Please do not share it with anyone.</p>
          <hr style="border: none; border-top: 1px solid #eeeeee; margin: 20px 0;">
          <p style="font-size: 12px; color: #888888;">If you did not request a password reset, please ignore this email. This message was sent automatically, please do not reply.</p>
        </div>
      </body>
    </html>
    """
    msg = MIMEText(body, "html")
    msg["Subject"] = subject
    msg["From"] = SMTP_EMAIL
    msg["To"] = to_email

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_EMAIL, SMTP_PASSWORD)
            server.sendmail(SMTP_EMAIL, to_email, msg.as_string())
    except Exception as e:
        print("Email sending failed:", e)


# ---------------- Routes ----------------

# Get user profile + designs
@router.get("/")
def get_profile(token: str = Depends(oauth2_scheme)):
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token")

    user_id = payload["sub"]

    user = supabase.table("users").select(
        "id, username, email, created_at"
    ).eq("id", user_id).single().execute()
    if not user.data:
        raise HTTPException(status_code=404, detail="User not found")

    designs = supabase.table("designs").select(
        "id, front_img_url, back_img_url, color, created_at"
    ).eq("user_id", user_id).execute()

    return {
        "user": user.data,
        "designs": designs.data if designs.data else []
    }

# Update profile info (only username here)
@router.put("/update")
def update_profile(data: UpdateProfileRequest, token: str = Depends(oauth2_scheme)):
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token")

    user_id = payload["sub"]

    update_data = {k: v for k, v in data.dict().items() if v is not None}
    if not update_data:
        raise HTTPException(status_code=400, detail="No fields to update")

    supabase.table("users").update(update_data).eq("id", user_id).execute()
    return {"message": "Profile updated successfully"}

# Forgot password - send OTP
@router.post("/forgot-password")
def forgot_password(request: ForgotPasswordRequest):
    user = supabase.table("users").select("id").eq("email", request.email).single().execute()
    if not user.data:
        raise HTTPException(status_code=404, detail="Email not found")

    otp = "".join(random.choices(string.digits, k=6))
    expiry = datetime.utcnow() + timedelta(minutes=5)

    otp_cache[request.email] = {"otp": otp, "expires": expiry, "verified": False}

    send_email(
        request.email,
        "Password Reset OTP",
        otp  # just pass the OTP; the function handles the HTML body
    )

    return {"message": "OTP sent to your email"}

# Verify OTP
@router.post("/verify-otp")
def verify_otp(request: VerifyOtpRequest):
    entry = otp_cache.get(request.email)
    if not entry or request.otp != entry["otp"]:
        raise HTTPException(status_code=400, detail="Invalid OTP")
    if datetime.utcnow() > entry["expires"]:
        del otp_cache[request.email]
        raise HTTPException(status_code=400, detail="OTP expired")

    otp_cache[request.email]["verified"] = True
    return {"message": "OTP verified"}

# Reset password 
@router.post("/reset-password")
def reset_password(request: NewPasswordRequest):
    entry = otp_cache.get(request.email)
    if not entry or not entry.get("verified"):
        raise HTTPException(status_code=400, detail="OTP not verified")

    new_hashed = hash_password(request.new_password)
    supabase.table("users").update({"password_hash": new_hashed}).eq("email", request.email).execute()

    del otp_cache[request.email]

    return {"message": "Password reset successful"}
