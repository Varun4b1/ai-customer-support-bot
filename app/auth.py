from authlib.integrations.starlette_client import OAuth
from fastapi import Request, HTTPException
from app.config import GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET

oauth = OAuth()

oauth.register(
    name="google",
    client_id=GOOGLE_CLIENT_ID,
    client_secret=GOOGLE_CLIENT_SECRET,
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
    client_kwargs={"scope": "openid email profile"},
)


async def get_current_user(request: Request):
    """Dependency — protects any route that requires login."""
    user = request.session.get("user")
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Not authenticated. Please login at /auth/login",
        )
    return user