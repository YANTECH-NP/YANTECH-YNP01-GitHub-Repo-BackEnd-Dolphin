"""Database operations for admin service."""
import boto3
import hashlib
from typing import Dict, List, Any, Optional
from .config import settings

def get_dynamodb_resource() -> Any:
    """Get DynamoDB resource client."""
    return boto3.resource(
        "dynamodb",
        region_name=settings.AWS_REGION
    )

def save_app_record(app_record: Dict[str, Any]) -> None:
    """Save application record to DynamoDB."""
    if not app_record or not isinstance(app_record, dict):
        raise ValueError("Invalid app_record: must be a non-empty dictionary")
    
    try:
        table = get_dynamodb_resource().Table(settings.APP_CONFIG_TABLE)
        table.put_item(Item=app_record)
    except Exception as e:
        raise RuntimeError(f"Failed to save app record: {str(e)}")

def get_all_apps() -> List[Dict[str, Any]]:
    """Retrieve all application records from DynamoDB."""
    try:
        table = get_dynamodb_resource().Table(settings.APP_CONFIG_TABLE)
        response = table.scan()
        return response.get("Items", [])
    except Exception as e:
        raise RuntimeError(f"Failed to retrieve apps: {str(e)}")

def update_app_record(app_id: str, app_record: Dict[str, Any]) -> None:
    """Update application record in DynamoDB."""
    if not app_id or not isinstance(app_id, str):
        raise ValueError("app_id must be a non-empty string")
    if not app_record or not isinstance(app_record, dict):
        raise ValueError("Invalid app_record: must be a non-empty dictionary")
    
    try:
        table = get_dynamodb_resource().Table(settings.APP_CONFIG_TABLE)
        table.put_item(Item=app_record)
    except Exception as e:
        raise RuntimeError(f"Failed to update app record: {str(e)}")

def delete_app_record(app_id: str) -> None:
    """Delete application record from DynamoDB."""
    if not app_id or not isinstance(app_id, str):
        raise ValueError("app_id must be a non-empty string")
    
    try:
        table = get_dynamodb_resource().Table(settings.APP_CONFIG_TABLE)
        table.delete_item(Key={"Application": app_id})
    except Exception as e:
        raise RuntimeError(f"Failed to delete app record: {str(e)}")

# API Key Management Functions

def save_api_key(api_key_record: Dict[str, Any]) -> None:
    """Save API key record to DynamoDB with hashed key for secure lookup."""
    if not api_key_record or not isinstance(api_key_record, dict):
        raise ValueError("Invalid api_key_record: must be a non-empty dictionary")
    
    # Ensure app_id is set for composite key
    if "app_id" not in api_key_record:
        api_key_record["app_id"] = api_key_record.get("application_id")
    
    # Generate key_hash for secure lookup (required by Lambda auth function)
    if "api_key" in api_key_record:
        api_key_value = api_key_record["api_key"]
        key_hash = hashlib.sha256(api_key_value.encode()).hexdigest()
        api_key_record["key_hash"] = key_hash
    
    try:
        table = get_dynamodb_resource().Table(settings.API_KEYS_TABLE)
        table.put_item(Item=api_key_record)
    except Exception as e:
        raise RuntimeError(f"Failed to save API key record: {str(e)}")

def get_api_keys_for_app(app_id: str) -> List[Dict[str, Any]]:
    """Get all API keys for a specific application."""
    if not app_id or not isinstance(app_id, str):
        raise ValueError("app_id must be a non-empty string")
    
    try:
        # First get the application to find the correct application_id
        apps = get_all_apps()
        app = next((app for app in apps if app.get("id") == app_id or app.get("Application") == app_id), None)
        if not app:
            return []
        
        # Use Application field for API key lookup
        app_application_id = app.get("Application", app_id)
        
        table = get_dynamodb_resource().Table(settings.API_KEYS_TABLE)
        response = table.query(
            KeyConditionExpression="app_id = :app_id",
            ExpressionAttributeValues={
                ":app_id": app_application_id
            }
        )
        return response.get("Items", [])
    except Exception as e:
        raise RuntimeError(f"Failed to retrieve API keys: {str(e)}")

def get_api_key_by_id(app_id: str, key_id: str) -> Optional[Dict[str, Any]]:
    """Get API key by app_id and key_id (composite key)."""
    if not app_id or not isinstance(app_id, str):
        raise ValueError("app_id must be a non-empty string")
    if not key_id or not isinstance(key_id, str):
        raise ValueError("key_id must be a non-empty string")
    
    try:
        # First get the application to find the correct application_id
        apps = get_all_apps()
        app = next((app for app in apps if app.get("id") == app_id or app.get("Application") == app_id), None)
        if not app:
            return None
        
        # Use Application field for API key lookup
        app_application_id = app.get("Application", app_id)
        
        table = get_dynamodb_resource().Table(settings.API_KEYS_TABLE)
        response = table.get_item(Key={"app_id": app_application_id, "id": key_id})
        return response.get("Item")
    except Exception as e:
        raise RuntimeError(f"Failed to retrieve API key: {str(e)}")

def delete_api_key(app_id: str, key_id: str) -> None:
    """Delete/revoke API key using composite key."""
    if not app_id or not isinstance(app_id, str):
        raise ValueError("app_id must be a non-empty string")
    if not key_id or not isinstance(key_id, str):
        raise ValueError("key_id must be a non-empty string")
    
    try:
        # First get the application to find the correct application_id
        apps = get_all_apps()
        app = next((app for app in apps if app.get("id") == app_id or app.get("Application") == app_id), None)
        if not app:
            raise RuntimeError("Application not found")
        
        # Use Application field for API key lookup
        app_application_id = app.get("Application", app_id)
        
        table = get_dynamodb_resource().Table(settings.API_KEYS_TABLE)
        table.delete_item(Key={"app_id": app_application_id, "id": key_id})
    except Exception as e:
        raise RuntimeError(f"Failed to delete API key: {str(e)}")
