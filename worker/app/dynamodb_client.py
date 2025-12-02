"""DynamoDB client operations for worker service."""
import boto3
from datetime import datetime, timezone
import uuid
from typing import Dict, Any, Optional
from . import config

dynamodb = boto3.resource(
    "dynamodb",
    region_name=config.AWS_REGION
)

def get_application_config(app_id: str) -> Optional[Dict[str, Any]]:
    """Get application configuration from DynamoDB."""
    if not app_id or not isinstance(app_id, str):
        raise ValueError("app_id must be a non-empty string")
    
    try:
        table = dynamodb.Table(config.APPLICATIONS_TABLE)
        response = table.get_item(Key={"Application": str(app_id)})
        return response.get("Item")
    except Exception as e:
        raise RuntimeError(f"Failed to get application config: {str(e)}")

def log_request(application_id: str, request_data: Any, status: str, error: Optional[str] = None) -> None:
    """Log request details to DynamoDB."""
    if not application_id or not isinstance(application_id, str):
        raise ValueError("application_id must be a non-empty string")
    if not status or not isinstance(status, str):
        raise ValueError("status must be a non-empty string")
    
    try:
        table = dynamodb.Table(config.REQUEST_LOG_TABLE)
        table.put_item(Item={
            "RecordID": str(uuid.uuid4()),
            "Application": str(application_id),
            "Timestamp": datetime.now(timezone.utc).isoformat(),
            "Status": str(status),
            "Error": str(error) if error else "None",
            "Request": str(request_data) if request_data else "",
        })
    except Exception as e:
        raise RuntimeError(f"Failed to log request: {str(e)}")

