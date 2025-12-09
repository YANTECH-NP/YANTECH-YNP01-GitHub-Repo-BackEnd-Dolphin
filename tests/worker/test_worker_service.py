"""Unit tests for Worker service."""
import pytest
import json
from unittest.mock import patch, MagicMock
import sys
import os

# Add worker directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../worker'))

@pytest.mark.unit
@patch('worker.app.main.dynamodb_client')
@patch('worker.app.main.notifier')
def test_process_email_message(mock_notifier, mock_db_client):
    """Test processing email notification message."""
    from worker.app.main import _process_message
    
    # Mock dependencies
    mock_db_client.get_application_config.return_value = {
        "SES-Domain-ARN": "arn:aws:ses:us-east-1:123456789012:identity/test.com"
    }
    
    # Test message
    message = {
        "Body": json.dumps({
            "Application": "test-app",
            "OutputType": "EMAIL",
            "Subject": "Test Subject",
            "Message": "Test message",
            "EmailAddresses": ["test@example.com"]
        })
    }
    
    result = _process_message(message)
    
    assert result is True
    mock_notifier.send_email.assert_called_once()
    mock_db_client.log_request.assert_called_with(
        "test-app", 
        json.loads(message["Body"]), 
        "delivered"
    )

@pytest.mark.unit
@patch('worker.app.main.dynamodb_client')
@patch('worker.app.main.notifier')
def test_process_sms_message(mock_notifier, mock_db_client):
    """Test processing SMS notification message."""
    from worker.app.main import _process_message
    
    # Mock dependencies
    mock_db_client.get_application_config.return_value = {
        "SNS-Topic-ARN": "arn:aws:sns:us-east-1:123456789012:test-topic"
    }
    
    # Test message
    message = {
        "Body": json.dumps({
            "Application": "test-app",
            "OutputType": "SMS",
            "Message": "Test SMS",
            "PhoneNumber": "+1234567890"
        })
    }
    
    result = _process_message(message)
    
    assert result is True
    mock_notifier.send_sns.assert_called_once()
    mock_db_client.log_request.assert_called_with(
        "test-app",
        json.loads(message["Body"]),
        "delivered"
    )

@pytest.mark.regression
@patch('worker.app.main.dynamodb_client')
@patch('worker.app.main.notifier')
def test_email_fallback_behavior(mock_notifier, mock_db_client):
    """Regression test: Ensure email fallback behavior remains consistent."""
    from worker.app.main import _process_message
    
    mock_db_client.get_application_config.return_value = {
        "SES-Domain-ARN": "arn:aws:ses:us-east-1:123456789012:identity/test.com"
    }
    
    # Test message with null EmailAddresses (should fallback to Recipient)
    message = {
        "Body": json.dumps({
            "Application": "test-app",
            "OutputType": "EMAIL",
            "Subject": "Test",
            "Message": "Test message",
            "EmailAddresses": [None],
            "Recipient": "fallback@example.com"
        })
    }
    
    result = _process_message(message)
    
    # Verify message was processed successfully
    assert result is True
    
    # Verify send_email was called
    mock_notifier.send_email.assert_called_once()
    
    # Verify fallback email was used
    call_args = mock_notifier.send_email.call_args[0]
    email_addresses = call_args[1]
    assert "fallback@example.com" in email_addresses