import os
from dotenv import load_dotenv

load_dotenv()

# AWS Configuration
AWS_REGION = os.getenv("AWS_REGION", "us-east-1")

# SQS Configuration - Production queue URLs (Standard Queues)
SQS_QUEUE_URL = os.getenv("SQS_QUEUE_URL", "https://sqs.us-east-1.amazonaws.com/588082972397/yantech-notification-queue-dev")
SQS_DLQ_URL = os.getenv("SQS_DLQ_URL", "https://sqs.us-east-1.amazonaws.com/588082972397/yantech-notification-dlq-dev")

# DynamoDB Tables - Match Terraform naming
APPLICATIONS_TABLE = os.getenv("APPLICATIONS_TABLE", "YANTECH-YNP01-AWS-DYNAMODB-APPLICATIONS-DEV")
REQUEST_LOG_TABLE = os.getenv("REQUEST_LOG_TABLE", "YANTECH-YNP01-AWS-DYNAMODB-REQUESTS-DEV")

# Logging Configuration
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

