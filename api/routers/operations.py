"""Operations router"""
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import JSONResponse
from schemas import OperationRequest, OperationResponse
from services.file_service import FileService
from validators import validate_operation_request
from tasks import process_csv_operation
from dependencies import get_current_user

router = APIRouter(prefix="/api", tags=["operations"])


@router.post("/perform-operation/", response_model=OperationResponse)
async def perform_operation(
    request: OperationRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Perform operations on uploaded CSV/Excel file
    """
    try:
        # Verify file exists
        FileService.find_file_by_id(request.file_id)
        
        # Validate operation and requirements
        validate_operation_request(
            request.operation,
            request.column,
            request.filter_conditions
        )
        
        # Create Celery task
        task = process_csv_operation.delay(
            file_id=request.file_id,
            operation=request.operation,
            column=request.column,
            filter_conditions=request.filter_conditions
        )
        
        return JSONResponse(
            status_code=200,
            content={
                "message": "Operation started",
                "task_id": task.id
            }
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Operation failed: {str(e)}"
        )

