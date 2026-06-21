from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.api.auth import router as auth_router

app = FastAPI(
    title="Document Copilot Backend",
    description="Production-style SEC Filing Research Assistant backend",
    version="0.1.0"
)

# Parse allowed origins from configuration
origins = [origin.strip() for origin in settings.allowed_origins.split(",") if origin.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router, prefix="/api")

@app.get("/")
async def status_check():
    return {
        "status": "ok",
        "phase": 1,
        "llm_provider": settings.llm_provider,
        "model_name": settings.model_name
    }
