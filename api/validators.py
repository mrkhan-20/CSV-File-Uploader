"""File validation functions"""
from fastapi import HTTPException, UploadFile
from pathlib import Path
import csv
import openpyxl
from config import ALLOWED_EXTENSIONS, MAX_FILE_SIZE


def validate_file(file: UploadFile) -> str:
    """Validate uploaded file and return file extension"""
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided")
    
    file_ext = Path(file.filename).suffix.lower()
    if file_ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail="Invalid file format. Only CSV and Excel files are allowed."
        )
    return file_ext


def validate_file_size(content: bytes) -> None:
    """Validate file size"""
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail="File size exceeds maximum allowed size of 50MB"
        )


def validate_csv_content(file_path: Path) -> None:
    """Validate CSV file can be read"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            next(reader)  # Try to read header
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid CSV format: {str(e)}"
        )


def validate_excel_content(file_path: Path) -> None:
    """Validate Excel file can be read"""
    try:
        wb = openpyxl.load_workbook(file_path, read_only=True)
        ws = wb.active
        # Try to read first row
        next(ws.iter_rows(min_row=1, max_row=1))
        wb.close()
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid Excel format: {str(e)}"
        )


def validate_operation(operation: str) -> None:
    """Validate operation type"""
    from config import VALID_OPERATIONS
    if operation not in VALID_OPERATIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid operation. Allowed operations: {', '.join(VALID_OPERATIONS)}"
        )


def validate_operation_request(operation: str, column: str = None, filter_conditions: dict = None) -> None:
    """Validate operation-specific requirements"""
    validate_operation(operation)
    
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

