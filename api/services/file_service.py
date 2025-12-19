"""File handling service"""
import uuid
from pathlib import Path
from fastapi import HTTPException, UploadFile
from config import UPLOAD_DIR, PROCESSED_DIR, ALLOWED_EXTENSIONS
from validators import (
    validate_file, 
    validate_file_size, 
    validate_csv_content, 
    validate_excel_content
)


class FileService:
    """Service for handling file operations"""
    
    @staticmethod
    async def save_uploaded_file(file: UploadFile) -> tuple[str, Path]:
        """
        Save uploaded file and return file_id and file_path
        
        Returns:
            tuple: (file_id, file_path)
        """
        # Validate file extension
        file_ext = validate_file(file)
        
        # Generate unique file ID
        file_id = str(uuid.uuid4())
        file_path = UPLOAD_DIR / f"{file_id}{file_ext}"
        
        # Read and validate file size
        content = await file.read()
        validate_file_size(content)
        
        # Save file
        with open(file_path, "wb") as f:
            f.write(content)
        
        # Validate content
        if file_ext == '.csv':
            validate_csv_content(file_path)
        else:
            validate_excel_content(file_path)
        
        return file_id, file_path
    
    @staticmethod
    def find_file_by_id(file_id: str) -> Path:
        """
        Find uploaded file by file_id with any allowed extension
        
        Returns:
            Path: Path to the file
            
        Raises:
            HTTPException: If file not found
        """
        for ext in ALLOWED_EXTENSIONS:
            potential_path = UPLOAD_DIR / f"{file_id}{ext}"
            if potential_path.exists():
                return potential_path
        
        raise HTTPException(
            status_code=404,
            detail="File not found"
        )
    
    @staticmethod
    def get_processed_file(filename: str) -> Path:
        """
        Get processed file by filename
        
        Returns:
            Path: Path to the processed file
            
        Raises:
            HTTPException: If file not found
        """
        file_path = PROCESSED_DIR / filename
        if not file_path.exists():
            raise HTTPException(status_code=404, detail="File not found")
        return file_path

