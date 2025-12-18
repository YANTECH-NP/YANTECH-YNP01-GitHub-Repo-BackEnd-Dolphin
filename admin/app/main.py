from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from fastapi.middleware.cors import CORSMiddleware
import secrets
import string
from datetime import datetime, timezone
from typing import Optional, List
from .db import save_app_record, get_all_apps, update_app_record, delete_app_record, save_api_key, get_api_keys_for_app, delete_api_key, get_api_key_by_id

app = FastAPI(
    title="Application API Key Manager",
    description="API for managing applications and their API keys",
    version="1.0.0"
)

# CORS middleware - matches server.py configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["Content-Type", "Authorization", "X-API-Key", "Accept"],
    expose_headers=["Content-Type", "X-Total-Count"],
    max_age=3600,
)

# Models matching server.py
class ApplicationCreate(BaseModel):
    App_name: str = Field(..., min_length=1, max_length=255)
    Application: str
    Email: str
    Domain: str

class ApplicationResponse(BaseModel):
    id: str
    name: str
    application_id: str
    email: str
    domain: str
    created_at: datetime
    updated_at: datetime

class APIKeyCreate(BaseModel):
    name: Optional[str] = None
    expires_at: Optional[datetime] = None

class APIKeyResponse(BaseModel):
    id: str
    api_key: str
    name: Optional[str]
    created_at: datetime
    expires_at: Optional[datetime]

class APIKeyInfo(BaseModel):
    id: str
    name: Optional[str]
    created_at: datetime
    expires_at: Optional[datetime]
    last_used_at: Optional[datetime]
    is_active: bool

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "online",
        "service": "Application API Key Manager",
        "version": "1.0.0"
    }

@app.get("/health")
async def health_check():
    """Detailed health check endpoint"""
    return {
        "status": "healthy",
        "service": "Application API Key Manager",
        "version": "1.0.0",
        "database": "connected",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }



@app.post("/app", response_model=ApplicationResponse, status_code=201)
async def create_application(app_data: ApplicationCreate):
    """Create a new application"""
    try:
        import uuid
        
        # Generate unique ID
        app_id = str(uuid.uuid4())
        now = datetime.now(timezone.utc)
        
        # Create application record using existing database schema
        app_record = {
            "Application": app_data.Application,  # Primary key for DynamoDB
            "App_name": app_data.App_name,
            "Email": app_data.Email,
            "Domain": app_data.Domain,
            "role": "client",  # Set role for Lambda authorizer
            "Status": "ACTIVE",  # Set status
            "id": app_id,  # Additional UUID for response
            "name": app_data.App_name,  # For server.py compatibility
            "application_id": app_data.Application,  # For server.py compatibility
            "email": app_data.Email,  # For server.py compatibility
            "domain": app_data.Domain,  # For server.py compatibility
            "created_at": now.isoformat(),
            "updated_at": now.isoformat()
        }
        
        save_app_record(app_record)
        
        # Return response matching server.py format
        return ApplicationResponse(
            id=app_id,
            name=app_data.App_name,
            application_id=app_data.Application,
            email=app_data.Email,
            domain=app_data.Domain,
            created_at=now,
            updated_at=now
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create application: {str(e)}")

@app.get("/apps", response_model=List[ApplicationResponse])
async def list_applications(skip: int = 0, limit: int = 100):
    """List all applications"""
    try:
        apps_data = get_all_apps()
        
        # Convert to response models matching server.py format
        apps = []
        for item in apps_data[skip:skip+limit]:
            apps.append(ApplicationResponse(
                id=item.get("id", item.get("Application", "")),
                name=item.get("name", item.get("App_name", "")),
                application_id=item.get("application_id", item.get("Application", "")),
                email=item.get("email", item.get("Email", "")),
                domain=item.get("domain", item.get("Domain", "")),
                created_at=datetime.fromisoformat(item.get("created_at", datetime.now(timezone.utc).isoformat())),
                updated_at=datetime.fromisoformat(item.get("updated_at", datetime.now(timezone.utc).isoformat()))
            ))
        
        return apps
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list applications: {str(e)}")

@app.get("/app/{app_id}", response_model=ApplicationResponse)
async def get_application(app_id: str):
    """Get a specific application"""
    try:
        apps = get_all_apps()
        app_item = next((app for app in apps if app.get("id") == app_id or app.get("Application") == app_id), None)
        
        if not app_item:
            raise HTTPException(status_code=404, detail="Application not found")
        
        return ApplicationResponse(
            id=app_item.get("id", app_item.get("Application", "")),
            name=app_item.get("name", app_item.get("App_name", "")),
            application_id=app_item.get("application_id", app_item.get("Application", "")),
            email=app_item.get("email", app_item.get("Email", "")),
            domain=app_item.get("domain", app_item.get("Domain", "")),
            created_at=datetime.fromisoformat(app_item.get("created_at", datetime.now(timezone.utc).isoformat())),
            updated_at=datetime.fromisoformat(app_item.get("updated_at", datetime.now(timezone.utc).isoformat()))
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get application: {str(e)}")

@app.put("/app/{app_id}", response_model=ApplicationResponse)
async def update_application(app_id: str, app_data: ApplicationCreate):
    """Update an existing application"""
    try:
        now = datetime.now(timezone.utc)
        
        # Create updated application record matching server.py format
        app_record = {
            "id": app_id,
            "name": app_data.App_name,
            "application_id": app_data.Application,
            "email": app_data.Email,
            "domain": app_data.Domain,
            "updated_at": now.isoformat()
        }
        
        update_app_record(app_id, app_record)
        
        # Get existing created_at
        apps = get_all_apps()
        existing_app = next((app for app in apps if app.get("id") == app_id or app.get("Application") == app_id), None)
        created_at = datetime.fromisoformat(existing_app.get("created_at", now.isoformat())) if existing_app else now
        
        return ApplicationResponse(
            id=app_id,
            name=app_data.App_name,
            application_id=app_data.Application,
            email=app_data.Email,
            domain=app_data.Domain,
            created_at=created_at,
            updated_at=now
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update application: {str(e)}")

@app.delete("/app/{app_id}", status_code=204)
async def delete_application(app_id: str):
    """Delete an application and all its API keys"""
    try:
        # Delete all API keys for this application
        try:
            keys = get_api_keys_for_app(app_id)
            for key in keys:
                delete_api_key(app_id, key["id"])
        except Exception:
            pass  # Continue even if no keys found
        
        # Delete the application
        delete_app_record(app_id)
        
        return None
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete application: {str(e)}")

# API Key Management Endpoints

@app.post("/app/{app_id}/api-key", response_model=APIKeyResponse, status_code=201)
async def generate_api_key(app_id: str, key_data: APIKeyCreate = APIKeyCreate()):
    """Generate a new API key for an application"""
    try:
        import uuid
        
        # Verify application exists
        apps = get_all_apps()
        app = next((app for app in apps if app.get("id") == app_id or app.get("Application") == app_id), None)
        if not app:
            raise HTTPException(status_code=404, detail="Application not found")
        
        # Generate a secure random API key matching server.py format
        api_key = f"sk_{secrets.token_urlsafe(32)}"
        key_id = str(uuid.uuid4())
        now = datetime.now(timezone.utc)
        
        api_key_record = {
            "app_id": app.get('Application', app.get('application_id', app_id)),  # Use Application field for Lambda lookup
            "id": key_id,
            "api_key": api_key,
            "name": key_data.name or f"API Key for {app.get('name', app.get('App_name', 'Application'))}",
            "created_at": now.isoformat(),
            "expires_at": key_data.expires_at.isoformat() if key_data.expires_at else None,
            "last_used_at": None,
            "is_active": True
        }
        
        save_api_key(api_key_record)
        
        return APIKeyResponse(
            id=key_id,
            api_key=api_key,
            name=api_key_record["name"],
            created_at=now,
            expires_at=key_data.expires_at
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate API key: {str(e)}")

@app.get("/app/{app_id}/api-keys", response_model=List[APIKeyInfo])
async def list_api_keys(app_id: str):
    """List all API keys for an application (without showing the actual keys)"""
    try:
        # Check if application exists
        apps = get_all_apps()
        app = next((app for app in apps if app.get("id") == app_id or app.get("Application") == app_id), None)
        if not app:
            raise HTTPException(status_code=404, detail="Application not found")
        
        keys = get_api_keys_for_app(app_id)
        return [
            APIKeyInfo(
                id=key["id"],
                name=key.get("name"),
                created_at=datetime.fromisoformat(key["created_at"]),
                expires_at=datetime.fromisoformat(key["expires_at"]) if key.get("expires_at") else None,
                last_used_at=datetime.fromisoformat(key["last_used_at"]) if key.get("last_used_at") else None,
                is_active=key.get("is_active", True)
            )
            for key in keys
        ]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list API keys: {str(e)}")

@app.delete("/app/{app_id}/api-key/{key_id}", status_code=204)
async def revoke_api_key(app_id: str, key_id: str):
    """Revoke (deactivate) an API key"""
    try:
        # Get the key to verify it exists
        key_record = get_api_key_by_id(app_id, key_id)
        if not key_record:
            raise HTTPException(status_code=404, detail="API key not found")
        
        delete_api_key(app_id, key_id)
        return None
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to revoke API key: {str(e)}")



