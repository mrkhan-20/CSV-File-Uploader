from fastapi import HTTPException
from pathlib import Path
import pandas as pd
from typing import Optional, Dict, Any, List
from celery.result import AsyncResult
from config import settings
from tasks import process_csv_operation, celery_app


class CSVService:
    """Service for CSV processing operations"""
    
    VALID_OPERATIONS = ["dedup", "unique", "filter"]
    
    @staticmethod
    def validate_operation(operation: str) -> None:
        """Validate operation type"""
        if operation not in CSVService.VALID_OPERATIONS:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid operation. Allowed operations: {', '.join(CSVService.VALID_OPERATIONS)}"
            )
    
    @staticmethod
    def validate_operation_requirements(
        operation: str,
        column: Optional[str] = None,
        filter_conditions: Optional[Dict] = None
    ) -> None:
        """Validate operation-specific requirements"""
        if operation == "unique" and not column:
            raise HTTPException(
                status_code=400,
                detail="Column name is required for 'unique' operation"
            )
        
        if operation == "filter" and not filter_conditions:
            raise HTTPException(
                status_code=400,
                detail="Filter conditions are required for 'filter' operation"
            )
    
    @staticmethod
    def start_operation(
        file_id: str,
        operation: str,
        column: Optional[str] = None,
        filter_conditions: Optional[Dict] = None
    ) -> str:
        """Start CSV processing operation and return task_id"""
        task = process_csv_operation.delay(
            file_id=file_id,
            operation=operation,
            column=column,
            filter_conditions=filter_conditions
        )
        return task.id
    
    @staticmethod
    def get_task_status(task_id: str, n: int = 100) -> Dict[str, Any]:
        """Get task status and results"""
        task_result = AsyncResult(task_id, app=celery_app)
        
        if task_result.state == "PENDING":
            return {
                "task_id": task_id,
                "status": "PENDING"
            }
        
        elif task_result.state == "SUCCESS":
            result = task_result.result
            processed_file = result.get("processed_file")
            
            # Read processed CSV and return first n records
            try:
                df = pd.read_csv(processed_file)
                data = df.head(n).to_dict(orient="records")
                
                return {
                    "task_id": task_id,
                    "status": "SUCCESS",
                    "result": {
                        "data": data,
                        "file_link": f"/processed/{Path(processed_file).name}"
                    }
                }
            except Exception as e:
                raise HTTPException(
                    status_code=500,
                    detail=f"Failed to read processed file: {str(e)}"
                )
        
        elif task_result.state == "FAILURE":
            error_msg = str(task_result.info) if task_result.info else "Unknown error"
            return {
                "task_id": task_id,
                "status": "FAILURE",
                "error": error_msg
            }
        
        else:
            return {
                "task_id": task_id,
                "status": task_result.state
            }


# Service instance
csv_service = CSVService()

