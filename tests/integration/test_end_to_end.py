"""Integration tests for the complete notification flow."""
import pytest
import json
from moto import mock_aws
import boto3

@pytest.mark.integration
@mock_aws
def test_complete_notification_flow(aws_credentials):
    """Test complete flow: Create app -> Generate API key -> Send notification."""
    
    # Setup AWS mocks
    dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
    sqs = boto3.client("sqs", region_name="us-east-1")
    sns = boto3.client("sns", region_name="us-east-1")
    ses = boto3.client("ses", region_name="us-east-1")
    
    # Create DynamoDB tables
    applications_table = dynamodb.create_table(
        TableName="test-applications",
        KeySchema=[{"AttributeName": "id", "KeyType": "HASH"}],
        AttributeDefinitions=[{"AttributeName": "id", "AttributeType": "S"}],
        BillingMode="PAY_PER_REQUEST"
    )
    
    api_keys_table = dynamodb.create_table(
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
    
    # Create SQS queue
    queue_response = sqs.create_queue(QueueName="test-queue")
    queue_url = queue_response["QueueUrl"]
    
    # Create SNS topic
    topic_response = sns.create_topic(Name="test-notifications")
    topic_arn = topic_response["TopicArn"]
    
    # Verify SES identity
    ses.verify_email_identity(EmailAddress="test@example.com")
    
    # Test data
    app_data = {
        "App_name": "Test Application",
        "Application": "test.app",
        "Email": "admin@test.app",
        "Domain": "test.app"
    }
    
    # 1. Create application (simulate admin service)
    applications_table.put_item(Item={
        "id": "test-app-001",
        "name": app_data["App_name"],
        "application_id": app_data["Application"],
        "email": app_data["Email"],
        "domain": app_data["Domain"],
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-01T00:00:00Z"
    })
    
    # 2. Generate API key (simulate admin service)
    api_keys_table.put_item(Item={
        "app_id": "test-app-001",
        "id": "key-001",
        "key_hash": "test-hash",
        "name": "Test API Key",
        "created_at": "2024-01-01T00:00:00Z",
        "is_active": True
    })
    
    # 3. Send notification to queue (simulate requestor service)
    notification = {
        "Application": "test-app-001",
        "OutputType": "EMAIL",
        "Subject": "Test Notification",
        "Message": "This is a test notification",
        "EmailAddresses": ["recipient@example.com"]
    }
    
    sqs.send_message(
        QueueUrl=queue_url,
        MessageBody=json.dumps(notification)
    )
    
    # 4. Verify message in queue
    messages = sqs.receive_message(QueueUrl=queue_url)
    assert "Messages" in messages
    assert len(messages["Messages"]) == 1
    
    received_message = json.loads(messages["Messages"][0]["Body"])
    assert received_message["Application"] == "test-app-001"
    assert received_message["OutputType"] == "EMAIL"
    
    # 5. Verify application exists in database
    app_response = applications_table.get_item(Key={"id": "test-app-001"})
    assert "Item" in app_response
    assert app_response["Item"]["name"] == "Test Application"

@pytest.mark.integration
@mock_aws
def test_database_operations(aws_credentials):
    """Test DynamoDB operations work correctly."""
    
    dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
    
    # Create table
    table = dynamodb.create_table(
        TableName="test-table",
        KeySchema=[{"AttributeName": "id", "KeyType": "HASH"}],
        AttributeDefinitions=[{"AttributeName": "id", "AttributeType": "S"}],
        BillingMode="PAY_PER_REQUEST"
    )
    
    # Test CRUD operations
    # Create
    table.put_item(Item={"id": "test-1", "name": "Test Item"})
    
    # Read
    response = table.get_item(Key={"id": "test-1"})
    assert "Item" in response
    assert response["Item"]["name"] == "Test Item"
    
    # Update
    table.update_item(
        Key={"id": "test-1"},
        UpdateExpression="SET #name = :name",
        ExpressionAttributeNames={"#name": "name"},
        ExpressionAttributeValues={":name": "Updated Item"}
    )
    
    # Verify update
    response = table.get_item(Key={"id": "test-1"})
    assert response["Item"]["name"] == "Updated Item"
    
    # Delete
    table.delete_item(Key={"id": "test-1"})
    
    # Verify deletion
    response = table.get_item(Key={"id": "test-1"})
    assert "Item" not in response