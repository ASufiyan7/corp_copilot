import pytest
from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient
from app.main import app
from app.database.session import get_db

# Reuse the db and engine fixtures from test_database to ensure clean database transaction isolation
from tests.test_database import db, engine

client = TestClient(app)

@pytest.fixture
def mock_supabase_get_user():
    """Mock the Supabase Auth Client's get_user method."""
    with patch("app.auth.dependencies.supabase_client.auth.get_user") as mock:
        yield mock

def test_auth_me_no_token():
    """Ensure accessing protected routes without an authorization header is forbidden."""
    response = client.get("/api/auth/me")
    assert response.status_code == 401  # HTTPBearer raises 401 when Authorization header is missing
    assert "Not authenticated" in response.json()["detail"]

def test_auth_me_invalid_token(mock_supabase_get_user):
    """Ensure invalid tokens result in a 401 Unauthorized response."""
    mock_supabase_get_user.side_effect = Exception("JWT signature verification failed")
    
    response = client.get("/api/auth/me", headers={"Authorization": "Bearer invalid_token_abc"})
    assert response.status_code == 401
    assert "Authentication failed" in response.json()["detail"]

def test_auth_me_valid_token(mock_supabase_get_user, db):
    """
    Ensure valid tokens allow request continuation, automatically
    create/sync the user profile locally, and return user profile details.
    """
    # Setup mock user response
    mock_user = MagicMock()
    mock_user.id = "4b5c7e12-25d2-432a-bc9e-884813fa1048"
    mock_user.email = "test_analyst@driftwood.com"
    
    mock_res = MagicMock()
    mock_res.user = mock_user
    mock_supabase_get_user.return_value = mock_res
    
    # Override get_db dependency to use the transactional database session fixture
    app.dependency_overrides[get_db] = lambda: db
    
    try:
        response = client.get("/api/auth/me", headers={"Authorization": "Bearer valid_token_123"})
        assert response.status_code == 200
        
        data = response.json()
        assert data["email"] == "test_analyst@driftwood.com"
        assert data["id"] == "4b5c7e12-25d2-432a-bc9e-884813fa1048"
        assert "created_at" in data
    finally:
        # Clear dependency overrides to prevent bleeding into other tests
        app.dependency_overrides.clear()
