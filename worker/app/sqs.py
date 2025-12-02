"""SQS operations for worker service."""
import boto3
from typing import List, Dict, Any
from . import config

session = boto3.session.Session(    
    region_name=config.AWS_REGION
)

sqs = session.client("sqs")

def poll_messages(max_messages: int = 5, wait_time: int = 10) -> List[Dict[str, Any]]:
    """Poll messages from SQS queue."""
    try:
        response = sqs.receive_message(
            QueueUrl=config.SQS_QUEUE_URL,
            MaxNumberOfMessages=max_messages,
            WaitTimeSeconds=wait_time
        )
        return response.get("Messages", [])
    except Exception as e:
        raise RuntimeError(f"Failed to poll SQS messages: {str(e)}")

def delete_message(receipt_handle: str) -> None:
    """Delete message from SQS queue."""
    if not receipt_handle or not isinstance(receipt_handle, str):
        raise ValueError("receipt_handle must be a non-empty string")
    
    try:
        sqs.delete_message(
            QueueUrl=config.SQS_QUEUE_URL,
            ReceiptHandle=receipt_handle
        )
    except Exception as e:
        raise RuntimeError(f"Failed to delete SQS message: {str(e)}")

