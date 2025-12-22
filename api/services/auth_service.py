"""Authentication service"""
import hashlib
import sqlite3
import jwt
from datetime import datetime, timedelta
from fastapi import HTTPException
from database import get_db

# JWT Configuration
SECRET_KEY = "your-secret-key-change-in-production"  # Should be in environment variable
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


class AuthService:
    """Service for handling authentication operations"""
    
    @staticmethod
    def hash_password(password: str) -> str:
        """Hash password using SHA256"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    @staticmethod
    def verify_password(password: str, password_hash: str) -> bool:
        """Verify password against hash"""
        return AuthService.hash_password(password) == password_hash
    
    @staticmethod
    def create_access_token(user_id: int, email: str) -> str:
        """Create JWT access token"""
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        payload = {
            "sub": str(user_id),
            "email": email,
            "exp": expire
        }
        return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    
    @staticmethod
    def verify_token(token: str) -> dict:
        """Verify JWT token and return payload"""
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            return payload
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="Token has expired")
        except jwt.InvalidTokenError:
            raise HTTPException(status_code=401, detail="Invalid token")
    
    @staticmethod
    def register_user(email: str, password: str, confirm_password: str) -> dict:
        """Register a new user"""
        if password != confirm_password:
            raise HTTPException(
                status_code=400,
                detail="Password and confirm password do not match"
            )
        
        password_hash = AuthService.hash_password(password)
        
        with get_db() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute(
                    "INSERT INTO users (email, password_hash) VALUES (?, ?)",
                    (email, password_hash)
                )
                user_id = cursor.lastrowid
                conn.commit()
                return {
                    "message": "Registration successful",
                    "user_id": str(user_id)
                }
            except sqlite3.IntegrityError:
                raise HTTPException(
                    status_code=400,
                    detail="Email already registered"
                )
    
    @staticmethod
    def login_user(email: str, password: str) -> dict:
        """Authenticate user and return JWT token"""
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id, email, password_hash FROM users WHERE email = ?",
                (email,)
            )
            user = cursor.fetchone()
        
        if not user or not AuthService.verify_password(password, user["password_hash"]):
            raise HTTPException(
                status_code=401,
                detail="Invalid email or password"
            )
        
        token = AuthService.create_access_token(user["id"], user["email"])
        return {
            "message": "Login successful",
            "token": token
        }

