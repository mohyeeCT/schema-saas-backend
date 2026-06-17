import os

from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from supabase import Client, create_client

security = HTTPBearer()


def get_supabase() -> Client:
    """Service role client for backend DB operations."""
    return create_client(
        os.environ["SUPABASE_URL"],
        os.environ["SUPABASE_SERVICE_ROLE_KEY"],
    )


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> dict:
    """Verify Supabase JWT and return the authenticated user."""
    token = credentials.credentials
    sb = create_client(
        os.environ["SUPABASE_URL"],
        os.environ["SUPABASE_ANON_KEY"],
    )
    try:
        result = sb.auth.get_user(token)
        if not result.user:
            raise HTTPException(status_code=401, detail="Invalid or expired token")
        return result.user
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
