"""Task status router"""
from fastapi import APIRouter, Query, HTTPException, Depends
from fastapi.responses import JSONResponse
from services.task_service import TaskService
from schemas import TaskStatusResponse
from dependencies import get_current_user

router = APIRouter(prefix="/api", tags=["tasks"])


@router.get("/task-status/", response_model=TaskStatusResponse)
async def task_status(
    task_id: str = Query(..., description="Task ID to check status"),
    n: int = Query(100, ge=1, le=10000, description="Number of records to return"),
    current_user: dict = Depends(get_current_user)
):
    """
    Check task status and get results
    """
    try:
        result = TaskService.get_task_status(task_id, n)
        return JSONResponse(status_code=200, content=result)
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch task status: {str(e)}"
        )

