"""File download router"""
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from services.file_service import FileService

router = APIRouter(tags=["files"])


@router.get("/processed/{filename}")
async def download_file(filename: str):
    """Download processed file"""
    try:
        file_path = FileService.get_processed_file(filename)
        return FileResponse(file_path, filename=filename)
    except HTTPException:
        raise

