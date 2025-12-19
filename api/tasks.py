from celery import Celery
import pandas as pd
from pathlib import Path
import uuid
from typing import Optional, Dict
from config import settings

# Celery configuration
celery_app = Celery(
    "csv_processor",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_BACKEND_URL
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


@celery_app.task(bind=True, name="tasks.process_csv_operation")
def process_csv_operation(
    self,
    file_id: str,
    operation: str,
    column: Optional[str] = None,
    filter_conditions: Optional[Dict] = None
):
    """
    Process CSV file with specified operation
    """
    try:
        # Update task state
        self.update_state(state="PROGRESS", meta={"status": "Reading CSV file"})
        
        # Read CSV file
        input_file = settings.UPLOAD_DIR / f"{file_id}.csv"
        df = pd.read_csv(input_file)
        
        # Perform operation
        self.update_state(state="PROGRESS", meta={"status": f"Performing {operation} operation"})
        
        if operation == "dedup":
            processed_df = perform_deduplication(df)
        
        elif operation == "unique":
            processed_df = perform_unique_extraction(df, column)
        
        elif operation == "filter":
            processed_df = perform_filtering(df, filter_conditions)
        
        else:
            raise ValueError(f"Unsupported operation: {operation}")
        
        # Save processed file
        self.update_state(state="PROGRESS", meta={"status": "Saving processed file"})
        
        output_filename = f"{uuid.uuid4()}_{operation}.csv"
        output_path = settings.PROCESSED_DIR / output_filename
        processed_df.to_csv(output_path, index=False)
        
        return {
            "status": "completed",
            "operation": operation,
            "processed_file": str(output_path),
            "original_rows": len(df),
            "processed_rows": len(processed_df)
        }
    
    except FileNotFoundError:
        raise Exception(f"File not found: {file_id}")
    
    except KeyError as e:
        raise Exception(f"Column not found: {str(e)}")
    
    except Exception as e:
        raise Exception(f"Processing failed: {str(e)}")


def perform_deduplication(df: pd.DataFrame) -> pd.DataFrame:
    """
    Remove duplicate rows from DataFrame
    """
    # Remove duplicate rows
    deduplicated_df = df.drop_duplicates()
    
    # Reset index
    deduplicated_df = deduplicated_df.reset_index(drop=True)
    
    return deduplicated_df


def perform_unique_extraction(df: pd.DataFrame, column: str) -> pd.DataFrame:
    """
    Extract unique values from a specific column
    """
    if column not in df.columns:
        raise KeyError(f"Column '{column}' not found in CSV file")
    
    # Get unique rows based on the specified column
    unique_df = df.drop_duplicates(subset=[column])
    
    # Reset index
    unique_df = unique_df.reset_index(drop=True)
    
    return unique_df


def perform_filtering(df: pd.DataFrame, filter_conditions: Dict) -> pd.DataFrame:
    """
    Filter DataFrame based on conditions
    
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
    
    filtered_df = df.copy()
    
    for column, condition in filter_conditions.items():
        if column not in df.columns:
            raise KeyError(f"Column '{column}' not found in CSV file")
        
        operator = condition.get("operator", "eq")
        value = condition.get("value")
        
        if value is None:
            raise ValueError(f"Value is required for filtering column '{column}'")
        
        # Apply filter based on operator
        if operator == "eq":
            filtered_df = filtered_df[filtered_df[column] == value]
        
        elif operator == "ne":
            filtered_df = filtered_df[filtered_df[column] != value]
        
        elif operator == "gt":
            filtered_df = filtered_df[filtered_df[column] > value]
        
        elif operator == "lt":
            filtered_df = filtered_df[filtered_df[column] < value]
        
        elif operator == "gte":
            filtered_df = filtered_df[filtered_df[column] >= value]
        
        elif operator == "lte":
            filtered_df = filtered_df[filtered_df[column] <= value]
        
        elif operator == "contains":
            filtered_df = filtered_df[
                filtered_df[column].astype(str).str.contains(str(value), na=False)
            ]
        
        elif operator == "in":
            if not isinstance(value, list):
                raise ValueError(f"'in' operator requires a list of values")
            filtered_df = filtered_df[filtered_df[column].isin(value)]
        
        else:
            raise ValueError(f"Unsupported operator: {operator}")
    
    # Reset index
    filtered_df = filtered_df.reset_index(drop=True)
    
    return filtered_df