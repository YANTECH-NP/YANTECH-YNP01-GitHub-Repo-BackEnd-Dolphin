"""Test configuration and fixtures."""
import os
import pytest
import boto3
from moto import mock_aws
from fastapi.testclient import TestClient
from faker import Faker

# Set test environment variables
os.environ["TESTING"] = "true"
os.environ["AWS_REGION"] = "us-east-1"
os.environ["APPLICATIONS_TABLE"] = "test-applications"
os.environ["API_KEYS_TABLE"] = "test-api-keys"
os.environ["SQS_QUEUE_URL"] = "https://sqs.us-east-1.amazonaws.com/123456789012/test-queue"
os.environ["ALLOWED_ORIGINS"] = "*"
os.environ["AWS_ACCESS_KEY_ID"] = "testing"
os.environ["AWS_SECRET_ACCESS_KEY"] = "testing"

fake = Faker()

@pytest.fixture(scope="function", autouse=True)
def aws_mocks():
    """Mock all AWS services and create tables."""
    with mock_aws():
        # Create DynamoDB tables
        dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
        
        # Create applications table
        dynamodb.create_table(
            TableName="test-applications",
            KeySchema=[{"AttributeName": "id", "KeyType": "HASH"}],
            AttributeDefinitions=[{"AttributeName": "id", "AttributeType": "S"}],
            BillingMode="PAY_PER_REQUEST"
        )
        
        # Create API keys table
        dynamodb.create_table(
            TableName="test-api-keys",
            KeySchema=[
                {"AttributeName": "app_id", "KeyType": "HASH"},
                {"AttributeName": "id", "KeyType": "RANGE"}
            ],
            AttributeDefinitions=[
                {"AttributeName": "app_id", "AttributeType": "S"},
                {"AttributeName": "id", "AttributeType": "S"}
            ],
            BillingMode="PAY_PER_REQUEST"
        )
        
        yield

@pytest.fixture
def client():
    """Admin service test client."""
    from admin.server import app
    return TestClient(app)

@pytest.fixture
def requestor_client():
    """Requestor service test client."""
    from requestor.app.main import app
    return TestClient(app)

@pytest.fixture
def sample_application():
    """Sample application data for testing."""
    return {
        "App_name": fake.company(),
        "Application": fake.domain_name(),
        "Email": fake.email(),
        "Domain": fake.domain_name()
    }

@pytest.fixture
def sample_notification():
    """Sample notification data for testing."""
    return {
        "Application": "test-app-001",
        "OutputType": "EMAIL",
        "Subject": fake.sentence(),
        "Message": fake.text(),
        "EmailAddresses": [fake.email()],
        "Recipient": fake.email(),
        "Interval": {
            "Once": True,
            "Days": [],
            "Weeks": [],
            "Months": [],
            "Years": []
        }
    }