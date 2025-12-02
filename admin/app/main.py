from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, EmailStr
from fastapi.middleware.cors import CORSMiddleware
import secrets
import string
from datetime import datetime, timezone
from typing import Optional, List
# Removed AWS services import - admin only handles app registration
from .db import save_app_record, get_all_apps, update_app_record, delete_app_record, save_api_key, get_api_keys_for_app, delete_api_key, get_api_key_by_id

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "*",  # Allow all origins for testing
        "http://yantech-frontend-admin.s3-website-us-east-1.amazonaws.com",
        "https://yantech-frontend-admin.s3.amazonaws.com"
    ],
    allow_credentials=False,  # Changed to False for S3 website compatibility
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization", "X-API-Key", "x-api-key"],
)

class AppRequest(BaseModel):
    App_name: str
    Application: str
    Email: EmailStr
    Domain: str

class APIKeyCreate(BaseModel):
    name: Optional[str] = None
    expires_at: Optional[str] = None

class APIKeyResponse(BaseModel):
    id: str
    api_key: str
    name: Optional[str]
    created_at: str
    expires_at: Optional[str]
    is_active: bool

class APIKeyInfo(BaseModel):
    id: str
    name: Optional[str]
    created_at: str
    expires_at: Optional[str]
    last_used_at: Optional[str]
    is_active: bool

@app.get("/health")
def health_check():
    return {"status": "ok", "service": "admin"}

@app.get("/debug/config")  # added debug endpoint"""  """
def debug_config():
    """Debug endpoint to check configuration"""
    from .config import settings
    return {
        "API_KEYS_TABLE": settings.API_KEYS_TABLE,
        "APP_CONFIG_TABLE": settings.APP_CONFIG_TABLE,
        "AWS_REGION": settings.AWS_REGION
    }

@app.options("/{path:path}")
def options_handler(path: str):
    """Handle CORS preflight requests"""
    return {"message": "OK"}



@app.post("/applications")
def register_application(app_req: AppRequest):
    try:
        # Create application record
        app_record = {
            "Application": app_req.Application,
            "App_name": app_req.App_name,
            "Email": app_req.Email,
            "Domain": app_req.Domain,
            "role": "client",
            "Status": "ACTIVE"
        }
        
        save_app_record(app_record)
        
        # Auto-generate initial API key
        alphabet = string.ascii_letters + string.digits + "_-"
        api_key = ''.join(secrets.choice(alphabet) for _ in range(32))
        
        api_key_record = {
            "app_id": app_req.Application,
            "id": f"key_{secrets.token_hex(8)}",
            "api_key": api_key,
            "name": "Default API Key",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "expires_at": None,
            "last_used_at": None,
            "is_active": True
        }
        
        save_api_key(api_key_record)
        
        # Return with API key for frontend
        return {
            "id": app_req.Application,
            "status": "created", 
            "application": app_req.Application,
            "message": "Application registered successfully",
            "apiKey": api_key,
            "apiKeyId": api_key_record["id"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/applications")
def list_registered_apps():
    try:
        return get_all_apps()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Frontend expects /apps endpoint
@app.get("/apps")
def list_apps_frontend():
    """Frontend-compatible endpoint"""
    try:
        return get_all_apps()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/app")
def create_app_frontend(app_req: AppRequest):
    """Frontend-compatible endpoint"""
    return register_application(app_req)

@app.put("/applications/{app_id}")
def update_application(app_id: str, app_req: AppRequest):
    """Update an existing application"""
    try:
        # Create updated application record
        app_record = {
            "Application": app_id,
            "App_name": app_req.App_name,
            "Email": app_req.Email,
            "Domain": app_req.Domain,
            "Status": "ACTIVE"
        }
        
        update_app_record(app_id, app_record)
        
        return {
            "status": "updated", 
            "application": app_id,
            "message": "Application updated successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/app/{app_id}")
def update_app_frontend(app_id: str, app_req: AppRequest):
    """Frontend-compatible endpoint"""
    return update_application(app_id, app_req)

@app.delete("/applications/{app_id}")
def delete_application(app_id: str):
    """Delete an application"""
    try:
        delete_app_record(app_id)
        
        return {
            "status": "deleted",
            "application": app_id,
            "message": "Application deleted successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/app/{app_id}")
def delete_app_frontend(app_id: str):
    """Frontend-compatible endpoint"""
    return delete_application(app_id)

# API Key Management Endpoints

@app.post("/app/{app_id}/api-key")
def create_api_key(app_id: str, key_data: APIKeyCreate):
    """Create new API key for application"""
    try:
        alphabet = string.ascii_letters + string.digits + "_-"
        api_key = ''.join(secrets.choice(alphabet) for _ in range(32))
        
        api_key_record = {
            "app_id": app_id,
            "id": f"key_{secrets.token_hex(8)}",
            "api_key": api_key,
            "name": key_data.name or "API Key",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "expires_at": key_data.expires_at,
            "last_used_at": None,
            "is_active": True
        }
        
        save_api_key(api_key_record)
        
        return APIKeyResponse(
            id=api_key_record["id"],
            api_key=api_key,
            name=api_key_record["name"],
            created_at=api_key_record["created_at"],
            expires_at=api_key_record["expires_at"],
            is_active=True
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/app/{app_id}/api-keys")
def get_application_api_keys(app_id: str) -> List[APIKeyInfo]:
    """Get all API keys for application"""
    try:
        keys = get_api_keys_for_app(app_id)
        return [
            APIKeyInfo(
                id=key["id"],
                name=key.get("name"),
                created_at=key["created_at"],
                expires_at=key.get("expires_at"),
                last_used_at=key.get("last_used_at"),
                is_active=key.get("is_active", True)
            )
            for key in keys
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/app/{app_id}/api-key/{key_id}")
def revoke_api_key(app_id: str, key_id: str):
    """Revoke/delete API key"""
    try:
        delete_api_key(app_id, key_id)
        return {
            "status": "revoked",
            "key_id": key_id,
            "message": "API key revoked successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/app/{app_id}/api-key/{key_id}/value")
def get_api_key_value(app_id: str, key_id: str):
    """Get API key value for admin interface - unauthenticated endpoint"""
    try:
        key_record = get_api_key_by_id(app_id, key_id)
        if not key_record:
            raise HTTPException(status_code=404, detail="API key not found")
        
        return {
            "api_key": key_record["api_key"],
            "id": key_record["id"],
            "is_active": key_record.get("is_active", True)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/app/{app_id}/api-key/{key_id}/regenerate")
def regenerate_api_key(app_id: str, key_id: str):
    """Regenerate API key"""
    try:
        # Get existing key info
        existing_key = get_api_key_by_id(app_id, key_id)
        if not existing_key:
            raise HTTPException(status_code=404, detail="API key not found")
        
        # Generate new key
        alphabet = string.ascii_letters + string.digits + "_-"
        new_api_key = ''.join(secrets.choice(alphabet) for _ in range(32))
        
        # Update key record
        updated_record = {
            **existing_key,
            "api_key": new_api_key,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "last_used_at": None
        }
        
        save_api_key(updated_record)
        
        return APIKeyResponse(
            id=updated_record["id"],
            api_key=new_api_key,
            name=updated_record.get("name"),
            created_at=updated_record["created_at"],
            expires_at=updated_record.get("expires_at"),
            is_active=updated_record.get("is_active", True)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



