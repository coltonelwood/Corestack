from fastapi import Depends, HTTPException, Request
from supabase import Client

from abf_api.deps.supabase import get_supabase


async def get_current_user(request: Request, db: Client = Depends(get_supabase)):
    """Extract and verify the JWT from the Authorization header."""
    auth_header = request.headers.get("authorization", "")
    if not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing authorization header")

    token = auth_header.removeprefix("Bearer ")

    try:
        res = db.auth.get_user(token)
        if res.user is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return res.user
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")
