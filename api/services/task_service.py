"""Task handling service"""
import csv
from pathlib import Path
from fastapi import HTTPException
from celery.result import AsyncResult
from config import PROCESSED_DIR


class TaskService:
    """Service for handling Celery task operations"""
    
    @staticmethod
    def get_task_status(task_id: str, n: int = 100) -> dict:
        """
        Get task status and results
        
        Args:
            task_id: Celery task ID
            n: Number of records to return (max 10000)
            
        Returns:
            dict: Task status information
        """
        task_result = AsyncResult(task_id)
        
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
                data = []
                with open(processed_file, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    for i, row in enumerate(reader):
                        if i >= n:
                            break
                        data.append(row)
                
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

