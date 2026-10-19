from typing import Any

from fastapi import HTTPException, Request, status

from .config import settings


async def get_current_user(request: Request) -> dict[str, Any]:
    """
    Sample host authentication dependency.
    Extracts authentication credentials from:
      1. Authorization header ('Bearer <token>')
      2. X-API-Key header ('<token>')
      3. Query parameter ('?token=<token>' or '?api_key=<token>')
      4. Browser cookie ('token' or 'access_token')

    This supports seamless testing via curl, Swagger UI, and standard browsers.
    """
    token: str | None = None

    # 1. Check Authorization header
    auth_header = request.headers.get("Authorization")
    if auth_header:
        parts = auth_header.split()
        if len(parts) == 2 and parts[0].lower() == "bearer":
            token = parts[1]
        elif len(parts) == 1:
            token = parts[0]

    # 2. Check X-API-Key header
    if not token:
        token = request.headers.get("X-API-Key")

    # 3. Check Query parameter
    if not token:
        token = request.query_params.get("token") or request.query_params.get("api_key")

    # 4. Check Cookie (useful for web browser navigation)
    if not token:
        token = request.cookies.get("token") or request.cookies.get("access_token")

    # If no token provided:
    if not token:
        if settings.dev_mode_auto_admin:
            return {
                "username": "dev-admin",
                "role": "admin",
                "is_admin": True,
                "auth_method": "dev_bypass",
            }
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=(
                "Authentication required. Provide an 'Authorization: Bearer <key>' header, "
                "'X-API-Key' header, or '?token=<key>' query parameter."
            ),
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Validate against known tokens
    if token == settings.admin_api_key:
        return {
            "username": "admin_user",
            "role": "admin",
            "is_admin": True,
            "auth_method": "admin_token",
        }

    if token == settings.user_api_key:
        return {
            "username": "standard_user",
            "role": "user",
            "is_admin": False,
            "auth_method": "user_token",
        }

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid API key or token.",
        headers={"WWW-Authenticate": "Bearer"},
    )


def is_admin(user: dict[str, Any]) -> bool:
    """
    Host authorization callback for Observability.
    Returns True if the user has administrator privileges, False otherwise.
    """
    return bool(user.get("role") == "admin" or user.get("is_admin") is True)
