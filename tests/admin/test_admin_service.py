"""Unit tests for Admin service."""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
import sys
import os

# Add admin directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../admin'))

# Using shared client fixture from conftest.py

@pytest.mark.unit
def test_health_endpoint(client):
    """Test health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "timestamp" in data

@pytest.mark.unit
def test_root_endpoint(client):
    """Test root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "online"
    assert "cors_origins" in data

@pytest.mark.unit
@patch('admin.server.dynamodb')
def test_create_application(mock_dynamodb, client, sample_application):
    """Test application creation."""
    # Mock DynamoDB table
    mock_table = MagicMock()
    mock_dynamodb.Table.return_value = mock_table
    
    response = client.post("/app", json=sample_application)
    assert response.status_code == 201
    
    data = response.json()
    assert "id" in data
    assert data["name"] == sample_application["App_name"]
    assert data["email"] == sample_application["Email"]
    
    # Verify DynamoDB was called
    mock_table.put_item.assert_called_once()

@pytest.mark.unit
@patch('admin.server.dynamodb')
def test_list_applications(mock_dynamodb, client):
    """Test listing applications."""
    # Mock DynamoDB response
    mock_table = MagicMock()
    mock_table.scan.return_value = {
        "Items": [{
            "id": "test-id",
            "name": "Test App",
            "application_id": "test.app",
            "email": "test@example.com",
            "domain": "example.com",
            "created_at": "2024-01-01T00:00:00+00:00",
            "updated_at": "2024-01-01T00:00:00+00:00"
        }]
    }
    mock_dynamodb.Table.return_value = mock_table
    
    response = client.get("/apps")
    assert response.status_code == 200
    
    data = response.json()
    assert len(data) == 1
    assert data[0]["name"] == "Test App"

@pytest.mark.unit
@patch('admin.server.dynamodb')
def test_generate_api_key(mock_dynamodb, client):
    """Test API key generation."""
    # Mock application exists
    mock_apps_table = MagicMock()
    mock_apps_table.get_item.return_value = {
        "Item": {"id": "test-app", "name": "Test App"}
    }
    
    mock_keys_table = MagicMock()
    
    def table_side_effect(table_name):
        if "applications" in table_name:
            return mock_apps_table
        return mock_keys_table
    
    mock_dynamodb.Table.side_effect = table_side_effect
    
    response = client.post("/app/test-app/api-key", json={"name": "Test Key"})
    assert response.status_code == 201
    
    data = response.json()
    assert "api_key" in data
    assert data["api_key"].startswith("sk_")
    assert data["name"] == "Test Key"
    
    # Verify API key was stored
    mock_keys_table.put_item.assert_called_once()

@pytest.mark.regression
@patch('admin.server.dynamodb')
def test_api_key_format_consistency(mock_dynamodb, client):
    """Regression test: Ensure API key format remains consistent."""
    # Mock application exists
    mock_apps_table = MagicMock()
    mock_apps_table.get_item.return_value = {
        "Item": {"id": "test-app", "name": "Test App"}
    }
    
    mock_keys_table = MagicMock()
    
    def table_side_effect(table_name):
        if "applications" in table_name:
            return mock_apps_table
        return mock_keys_table
    
    mock_dynamodb.Table.side_effect = table_side_effect
    
    response = client.post("/app/test-app/api-key")
    assert response.status_code == 201
    
    data = response.json()
    api_key = data["api_key"]
    
    # Regression check: API key format must remain consistent
    assert api_key.startswith("sk_")
    assert len(api_key) > 40  # Ensure sufficient length
    assert "_" in api_key  # Ensure separator exists

@pytest.mark.unit
def test_cors_headers(client):
    """Test CORS headers are present."""
    response = client.options("/apps")
    assert response.status_code == 200
    
    # Check CORS headers
    headers = response.headers
    assert "access-control-allow-origin" in headers
    assert "access-control-allow-methods" in headers