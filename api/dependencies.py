"""Dependencies for route protection"""
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from services.auth_service import AuthService

security = HTTPBearer()


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Dependency to get current authenticated user from JWT token"""
    token = credentials.credentials
    try:
        payload = AuthService.verify_token(token)
        return {
            "user_id": payload.get("sub"),
            "email": payload.get("email")
        }
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        )

