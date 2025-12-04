"""Unit tests for Requestor service."""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
import sys
import os

# Add requestor directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../requestor'))

# Using shared requestor_client fixture from conftest.py

@pytest.fixture
def client(requestor_client):
    """Alias for requestor client."""
    return requestor_client

@pytest.mark.unit
def test_health_endpoint(client):
    """Test health check endpoint."""
    # Mock app state as ready
    with patch('requestor.app.main.app_state') as mock_state:
        mock_state.ready = True
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert data["ready"] is True

@pytest.mark.unit
def test_health_endpoint_not_ready(client):
    """Test health check when service not ready."""
    with patch('requestor.app.main.app_state') as mock_state:
        mock_state.ready = False
        response = client.get("/health")
        assert response.status_code == 503

@pytest.mark.unit
@patch('requestor.app.main.send_message_to_queue')
def test_notifications_endpoint(mock_send_message, client, sample_notification):
    """Test notifications endpoint."""
    # Mock SQS response
    mock_send_message.return_value = {"MessageId": "test-message-id"}
    
    response = client.post("/notifications", json=sample_notification)
    assert response.status_code == 200
    
    data = response.json()
    assert data["message_id"] == "test-message-id"
    assert data["status"] == "queued"
    assert "processing_time_ms" in data
    
    # Verify SQS was called
    mock_send_message.assert_called_once_with(sample_notification)

@pytest.mark.unit
def test_auth_endpoint(client):
    """Test auth endpoint."""
    response = client.post("/auth", json={"username": "test"})
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert data["token"] == "handled_by_api_gateway"

@pytest.mark.regression
@patch('requestor.app.main.send_message_to_queue')
def test_notification_request_format_consistency(mock_send_message, client):
    """Regression test: Ensure notification request format remains consistent."""
    mock_send_message.return_value = {"MessageId": "test-id"}
    
    # Test with minimal required fields
    notification = {
        "Application": "test-app",
        "OutputType": "EMAIL",
        "Subject": "Test",
        "Message": "Test message",
        "EmailAddresses": ["test@example.com"]
    }
    
    response = client.post("/notifications", json=notification)
    assert response.status_code == 200
    
    # Verify the exact format passed to SQS
    called_args = mock_send_message.call_args[0][0]
    assert called_args["Application"] == "test-app"
    assert called_args["OutputType"] == "EMAIL"
    assert "Subject" in called_args
    assert "Message" in called_args

@pytest.mark.unit
@patch('requestor.app.main.send_message_to_queue')
def test_notifications_error_handling(mock_send_message, client, sample_notification):
    """Test error handling in notifications endpoint."""
    # Mock SQS failure
    mock_send_message.side_effect = Exception("SQS connection failed")
    
    response = client.post("/notifications", json=sample_notification)
    assert response.status_code == 500

@pytest.mark.unit
def test_cors_headers(client):
    """Test CORS middleware is configured."""
    response = client.get("/health")
    assert response.status_code == 200