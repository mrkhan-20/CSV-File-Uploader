"""Pydantic models/schemas for request/response validation"""
from pydantic import BaseModel
from typing import Optional, Dict, List, Any


class OperationRequest(BaseModel):
    """Request schema for performing operations on uploaded files"""
    file_id: str
    operation: str
    column: Optional[str] = None
    filter_conditions: Optional[Dict] = None


class UploadResponse(BaseModel):
    """Response schema for file upload"""
    message: str
    file_id: str


class OperationResponse(BaseModel):
    """Response schema for operation initiation"""
    message: str
    task_id: str


class TaskStatusResponse(BaseModel):
    """Response schema for task status"""
    task_id: str
    status: str
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

