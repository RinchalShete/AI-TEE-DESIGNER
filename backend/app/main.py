from fastapi import FastAPI
from app.api.routes import router as api_router
from app.api.auth import router as auth_router  # import auth router
from app.api.profile import router as profile_router
from app.config import CLOUDINARY_CLOUD_NAME, CLOUDINARY_API_KEY, CLOUDINARY_API_SECRET

app = FastAPI()

# Include your API routers
app.include_router(api_router)  # main routes
app.include_router(auth_router)  # auth routes under /auth
app.include_router(profile_router) 

@app.get("/health")
async def health():
    return {"status": "ok"}
