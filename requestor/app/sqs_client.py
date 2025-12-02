"""SQS client operations for requestor service."""
import boto3
import json
from typing import Dict, Any
from .config import settings

def get_sqs_client() -> Any:
    """Get SQS client."""
    return boto3.client(
        "sqs",
        region_name=settings.AWS_REGION
    )

def send_message_to_queue(message: Dict[str, Any]) -> Dict[str, Any]:
    """Send message to SQS queue."""
    import logging
    import time
    
    if not message or not isinstance(message, dict):
        raise ValueError("message must be a non-empty dictionary")
    
    try:
        # Time SQS client creation
        client_start = time.time()
        sqs = get_sqs_client()
        client_time = time.time() - client_start
        logging.info(f"🔧 SQS client created in {client_time:.3f}s")
        
        # Time JSON serialization
        json_start = time.time()
        message_body = json.dumps(message)
        json_time = time.time() - json_start
        logging.info(f"📝 JSON serialization completed in {json_time:.3f}s")
        
        # Time SQS send operation
        send_start = time.time()
        response = sqs.send_message(
            QueueUrl=settings.SQS_QUEUE_URL,
            MessageBody=message_body
        )
        send_time = time.time() - send_start
        logging.info(f"📤 SQS send_message completed in {send_time:.3f}s")
        
        return response
    except Exception as e:
        logging.error(f"❌ SQS operation failed: {str(e)}")
        raise RuntimeError(f"Failed to send message to SQS: {str(e)}")
