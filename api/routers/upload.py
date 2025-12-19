"""Upload file router"""
from fastapi import APIRouter, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from services.file_service import FileService
from schemas import UploadResponse

router = APIRouter(prefix="/api", tags=["upload"])


@router.post("/upload-csv/", response_model=UploadResponse)
async def upload_csv(file: UploadFile = File(...)):
    """
    Upload a CSV or Excel file for processing
    """
    try:
        file_id, _ = await FileService.save_uploaded_file(file)
        
        return JSONResponse(
            status_code=200,
            content={
                "message": "File uploaded successfully",
                "file_id": file_id
            }
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

