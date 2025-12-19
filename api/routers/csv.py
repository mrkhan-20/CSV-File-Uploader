from fastapi import APIRouter, File, UploadFile, HTTPException, Query
from fastapi.responses import JSONResponse
import uuid
from typing import Optional

from models.schemas import OperationRequest, UploadResponse, OperationResponse, TaskStatusResponse
from services.file_service import file_service
from services.csv_service import csv_service


router = APIRouter(prefix="/api", tags=["CSV"])


@router.post("/upload-csv/", response_model=UploadResponse)
async def upload_csv(file: UploadFile = File(...)):
    """
    Upload a CSV file for processing
    """
    try:
        # Validate file
        file_service.validate_csv_file(file)
        
        # Generate unique file ID
        file_id = str(uuid.uuid4())
        
        # Read file content
        content = await file.read()
        
        # Validate file size
        await file_service.validate_file_size(content)
        
        # Validate CSV format
        file_service.validate_csv_format(content)
        
        # Save file
        await file_service.save_uploaded_file(file_id, content)
        
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


@router.post("/perform-operation/", response_model=OperationResponse)
async def perform_operation(request: OperationRequest):
    """
    Perform operations on uploaded CSV file
    """
    try:
        # Validate file exists
        if not file_service.file_exists(request.file_id):
            raise HTTPException(
                status_code=404,
                detail="File not found."
            )
        
        # Validate operation
        csv_service.validate_operation(request.operation)
        
        # Validate operation-specific requirements
        csv_service.validate_operation_requirements(
            request.operation,
            request.column,
            request.filter_conditions
        )
        
        # Start operation
        task_id = csv_service.start_operation(
            file_id=request.file_id,
            operation=request.operation,
            column=request.column,
            filter_conditions=request.filter_conditions
        )
        
        return JSONResponse(
            status_code=200,
            content={
                "message": "Operation started",
                "task_id": task_id
            }
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Operation failed: {str(e)}"
        )


@router.get("/task-status/")
async def task_status(
    task_id: str = Query(..., description="Task ID to check status"),
    n: int = Query(100, ge=1, le=10000, description="Number of records to return")
):
    """
    Check task status and get results
    """
    try:
        result = csv_service.get_task_status(task_id, n)
        return JSONResponse(status_code=200, content=result)
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch task status: {str(e)}"
        )

