from fastapi import UploadFile, HTTPException
from pathlib import Path
import pandas as pd
from io import BytesIO
from typing import Optional
from config import settings


class FileService:
    """Service for file operations"""
    
    @staticmethod
    def validate_csv_file(file: UploadFile) -> None:
        """Validate uploaded CSV file"""
        if not file.filename:
            raise HTTPException(status_code=400, detail="No file provided")
        
        file_ext = Path(file.filename).suffix.lower()
        if file_ext not in settings.ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=400,
                detail="Invalid file format. Only CSV files are allowed."
            )
    
    @staticmethod
    async def validate_file_size(content: bytes) -> None:
        """Validate file size"""
        if len(content) > settings.MAX_FILE_SIZE:
            raise HTTPException(
                status_code=400,
                detail=f"File size exceeds maximum allowed size of {settings.MAX_FILE_SIZE / (1024 * 1024)}MB"
            )
    
    @staticmethod
    def validate_csv_format(content: bytes) -> None:
        """Validate CSV format by trying to read it"""
        try:
            pd.read_csv(BytesIO(content))
        except Exception as e:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid CSV format: {str(e)}"
            )
    
    @staticmethod
    async def save_uploaded_file(file_id: str, content: bytes) -> Path:
        """Save uploaded file and return file path"""
        file_path = settings.UPLOAD_DIR / f"{file_id}.csv"
        with open(file_path, "wb") as f:
            f.write(content)
        return file_path
    
    @staticmethod
    def file_exists(file_id: str) -> bool:
        """Check if file exists"""
        file_path = settings.UPLOAD_DIR / f"{file_id}.csv"
        return file_path.exists()
    
    @staticmethod
    def get_file_path(file_id: str) -> Path:
        """Get file path for a given file_id"""
        return settings.UPLOAD_DIR / f"{file_id}.csv"


# Service instance
file_service = FileService()

