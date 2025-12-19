from pydantic import BaseModel
from typing import Optional, Dict, List, Any


class OperationRequest(BaseModel):
    """Request model for CSV operations"""
    file_id: str
    operation: str
    column: Optional[str] = None
    filter_conditions: Optional[Dict[str, Dict[str, Any]]] = None


class UploadResponse(BaseModel):
    """Response model for file upload"""
    message: str
    file_id: str


class OperationResponse(BaseModel):
    """Response model for operation start"""
    message: str
    task_id: str


class TaskStatusResponse(BaseModel):
    """Response model for task status"""
    task_id: str
    status: str
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


class RootResponse(BaseModel):
    """Response model for root endpoint"""
    message: str
    version: str
    endpoints: Dict[str, str]

