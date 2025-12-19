from celery import Celery
import csv
import openpyxl
from pathlib import Path
import uuid
from typing import Optional, Dict, List, Any

# Celery configuration
celery_app = Celery(
    "csv_processor",
    broker="redis://localhost:6379/0",
    backend="redis://localhost:6379/0"
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=3600,  # 1 hour
    task_soft_time_limit=3000,  # 50 minutes
)

UPLOAD_DIR = Path("uploads")
PROCESSED_DIR = Path("processed")


def read_csv_file(file_path: Path) -> tuple[List[str], List[List[str]]]:
    """Read CSV file and return headers and data"""
    with open(file_path, 'r', encoding='utf-8', newline='') as f:
        reader = csv.reader(f)
        headers = next(reader)
        data = list(reader)
    return headers, data


def read_excel_file(file_path: Path) -> tuple[List[str], List[List[str]]]:
    """Read Excel file and return headers and data"""
    wb = openpyxl.load_workbook(file_path, read_only=True)
    ws = wb.active
    
    rows = list(ws.iter_rows(values_only=True))
    headers = [str(cell) if cell is not None else '' for cell in rows[0]]
    data = [[str(cell) if cell is not None else '' for cell in row] for row in rows[1:]]
    
    wb.close()
    return headers, data


def write_csv_file(file_path: Path, headers: List[str], data: List[List[str]]) -> None:
    """Write data to CSV file"""
    with open(file_path, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        writer.writerows(data)


def find_input_file(file_id: str) -> Path:
    """Find input file with any supported extension"""
    for ext in ['.csv', '.xlsx', '.xls']:
        file_path = UPLOAD_DIR / f"{file_id}{ext}"
        if file_path.exists():
            return file_path
    raise FileNotFoundError(f"File not found: {file_id}")


@celery_app.task(bind=True, name="tasks.process_csv_operation")
def process_csv_operation(
    self,
    file_id: str,
    operation: str,
    column: Optional[str] = None,
    filter_conditions: Optional[Dict] = None
):
    """
    Process CSV/Excel file with specified operation
    """
    try:
        # Update task state
        self.update_state(state="PROGRESS", meta={"status": "Reading file"})
        
        # Find and read input file
        input_file = find_input_file(file_id)
        
        if input_file.suffix == '.csv':
            headers, data = read_csv_file(input_file)
        else:
            headers, data = read_excel_file(input_file)
        
        # Perform operation
        self.update_state(state="PROGRESS", meta={"status": f"Performing {operation} operation"})
        
        if operation == "dedup":
            processed_data = perform_deduplication(headers, data)
        
        elif operation == "unique":
            processed_data = perform_unique_extraction(headers, data, column)
        
        elif operation == "filter":
            processed_data = perform_filtering(headers, data, filter_conditions)
        
        else:
            raise ValueError(f"Unsupported operation: {operation}")
        
        # Save processed file
        self.update_state(state="PROGRESS", meta={"status": "Saving processed file"})
        
        output_filename = f"{uuid.uuid4()}_{operation}.csv"
        output_path = PROCESSED_DIR / output_filename
        write_csv_file(output_path, headers, processed_data)
        
        return {
            "status": "completed",
            "operation": operation,
            "processed_file": str(output_path),
            "original_rows": len(data),
            "processed_rows": len(processed_data)
        }
    
    except FileNotFoundError as e:
        raise Exception(f"File not found: {file_id}")
    
    except KeyError as e:
        raise Exception(f"Column not found: {str(e)}")
    
    except Exception as e:
        raise Exception(f"Processing failed: {str(e)}")


def perform_deduplication(headers: List[str], data: List[List[str]]) -> List[List[str]]:
    """
    Remove duplicate rows from data
    """
    seen = set()
    unique_data = []
    
    for row in data:
        # Convert row to tuple for hashing
        row_tuple = tuple(row)
        if row_tuple not in seen:
            seen.add(row_tuple)
            unique_data.append(row)
    
    return unique_data


def perform_unique_extraction(headers: List[str], data: List[List[str]], column: str) -> List[List[str]]:
    """
    Extract unique values from a specific column
    """
    if column not in headers:
        raise KeyError(f"Column '{column}' not found in file")
    
    column_index = headers.index(column)
    seen = set()
    unique_data = []
    
    for row in data:
        if column_index < len(row):
            value = row[column_index]
            if value not in seen:
                seen.add(value)
                unique_data.append(row)
    
    return unique_data


def perform_filtering(headers: List[str], data: List[List[str]], filter_conditions: Dict) -> List[List[str]]:
    """
    Filter data based on conditions
    
    Expected filter_conditions format:
    {
        "column_name": {
            "operator": "eq|ne|gt|lt|gte|lte|contains|in",
            "value": "value_to_compare"
        }
    }
    """
    if not filter_conditions:
        raise ValueError("Filter conditions cannot be empty")
    
    # Validate columns
    for column in filter_conditions.keys():
        if column not in headers:
            raise KeyError(f"Column '{column}' not found in file")
    
    filtered_data = []
    
    for row in data:
        if matches_filters(row, headers, filter_conditions):
            filtered_data.append(row)
    
    return filtered_data


def matches_filters(row: List[str], headers: List[str], filter_conditions: Dict) -> bool:
    """Check if a row matches all filter conditions"""
    for column, condition in filter_conditions.items():
        column_index = headers.index(column)
        
        if column_index >= len(row):
            return False
        
        cell_value = row[column_index]
        operator = condition.get("operator", "eq")
        filter_value = condition.get("value")
        
        if filter_value is None:
            raise ValueError(f"Value is required for filtering column '{column}'")
        
        # Try to convert to numeric if possible
        try:
            cell_numeric = float(cell_value)
            filter_numeric = float(filter_value)
            is_numeric = True
        except (ValueError, TypeError):
            is_numeric = False
            cell_numeric = None
            filter_numeric = None
        
        # Apply filter based on operator
        if operator == "eq":
            if is_numeric:
                if not (cell_numeric == filter_numeric):
                    return False
            else:
                if not (cell_value == str(filter_value)):
                    return False
        
        elif operator == "ne":
            if is_numeric:
                if not (cell_numeric != filter_numeric):
                    return False
            else:
                if not (cell_value != str(filter_value)):
                    return False
        
        elif operator == "gt":
            if not is_numeric:
                raise ValueError(f"Cannot use 'gt' operator on non-numeric column '{column}'")
            if not (cell_numeric > filter_numeric):
                return False
        
        elif operator == "lt":
            if not is_numeric:
                raise ValueError(f"Cannot use 'lt' operator on non-numeric column '{column}'")
            if not (cell_numeric < filter_numeric):
                return False
        
        elif operator == "gte":
            if not is_numeric:
                raise ValueError(f"Cannot use 'gte' operator on non-numeric column '{column}'")
            if not (cell_numeric >= filter_numeric):
                return False
        
        elif operator == "lte":
            if not is_numeric:
                raise ValueError(f"Cannot use 'lte' operator on non-numeric column '{column}'")
            if not (cell_numeric <= filter_numeric):
                return False
        
        elif operator == "contains":
            if str(filter_value).lower() not in cell_value.lower():
                return False
        
        elif operator == "in":
            if not isinstance(filter_value, list):
                raise ValueError(f"'in' operator requires a list of values")
            if cell_value not in [str(v) for v in filter_value]:
                return False
        
        else:
            raise ValueError(f"Unsupported operator: {operator}")
    
    return True