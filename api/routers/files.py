"""File download router"""
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import FileResponse
from services.file_service import FileService
from dependencies import get_current_user

router = APIRouter(prefix="/api", tags=["files"])


@router.get("/processed/{filename}")
async def download_file(
    filename: str,
    current_user: dict = Depends(get_current_user)
):
    """Download processed file"""
    try:
        file_path = FileService.get_processed_file(filename)
        return FileResponse(file_path, filename=filename)
    except HTTPException:
        raise

