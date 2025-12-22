"""Authentication router"""
from fastapi import APIRouter, Form, HTTPException
from fastapi.responses import JSONResponse
from services.auth_service import AuthService

router = APIRouter(prefix="/api", tags=["auth"])


@router.post("/register/")
async def register(
    email: str = Form(...),
    password: str = Form(...),
    confirm_password: str = Form(...)
):
    """
    Register a new user
    """
    try:
        result = AuthService.register_user(email, password, confirm_password)
        return JSONResponse(status_code=200, content=result)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Registration failed: {str(e)}"
        )


@router.post("/login/")
async def login(
    email: str = Form(...),
    password: str = Form(...)
):
    """
    Login user and get JWT token
    """
    try:
        result = AuthService.login_user(email, password)
        return JSONResponse(status_code=200, content=result)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Login failed: {str(e)}"
        )

