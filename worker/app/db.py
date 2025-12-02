"""Database operations for worker service."""
import boto3
from datetime import datetime, timezone
from typing import Any
from . import config

dynamodb = boto3.resource(
    "dynamodb",
    region_name=config.AWS_REGION
)

def log_request(app_id: str, message: Any, status: str, error: str = "") -> None:
    """Log request to DynamoDB."""
    if not app_id or not isinstance(app_id, str):
        raise ValueError("app_id must be a non-empty string")
    if not status or not isinstance(status, str):
        raise ValueError("status must be a non-empty string")
    
    try:
        table = dynamodb.Table(config.REQUEST_LOG_TABLE)
        table.put_item(Item={
            "Application": str(app_id),
            "Timestamp": datetime.now(timezone.utc).isoformat(),
            "Status": str(status),
            "Payload": str(message) if message else "",
            "Error": str(error) if error else ""
        })
    except Exception as e:
        raise RuntimeError(f"Failed to log request: {str(e)}")

