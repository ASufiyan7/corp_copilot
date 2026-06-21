from fastapi import APIRouter, Depends
from pydantic import BaseModel, ConfigDict
from uuid import UUID
from datetime import datetime

from app.auth.dependencies import get_current_user
from app.database.models import Profile

router = APIRouter(prefix="/auth", tags=["auth"])

class UserProfileResponse(BaseModel):
    id: UUID
    email: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

@router.get("/me", response_model=UserProfileResponse)
async def get_me(current_user: Profile = Depends(get_current_user)):
    """
    Retrieve the currently authenticated user's profile.
    This serves as our verification endpoint to confirm authentication works.
    """
    return current_user
