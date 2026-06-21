import uuid
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from supabase import create_client, Client

from app.config import settings
from app.database.session import get_db
from app.database import chats
from app.database.models import Profile

security = HTTPBearer()

# Initialize Supabase client on the backend using service role key to manage operations securely
supabase_client: Client = create_client(settings.supabase_url, settings.supabase_service_role_key)

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> Profile:
    """
    FastAPI dependency that extracts the JWT token from the Authorization header,
    verifies it against Supabase Auth, resolves/syncs the profile in the local
    database, and returns the Profile database model instance.
    """
    token = credentials.credentials
    try:
        # Verify the JWT using Supabase Auth
        res = supabase_client.auth.get_user(token)
        if not res or not res.user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired authentication token"
            )
        user = res.user
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Authentication failed: {str(e)}"
        )

    # Convert the string user ID to a UUID
    try:
        user_uuid = uuid.UUID(user.id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid user ID format in token"
        )

    # Fetch profile from local database, creating one if not exists
    profile = chats.get_profile(db, user_uuid)
    if not profile:
        # Sync the profile record from Supabase auth to our local database
        email = user.email or ""
        profile = chats.create_profile(db, email=email, profile_id=user_uuid)
        
    return profile
