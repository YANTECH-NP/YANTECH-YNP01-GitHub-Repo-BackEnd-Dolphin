import boto3
import json
from . import config , logger

sqs = boto3.client(
    "sqs",
    region_name=config.AWS_REGION
)

def poll_messages(max_messages=1):
    logger.log(f"Polling messages from QueueUrl: {config.SQS_QUEUE_URL}")
    response = sqs.receive_message(
        QueueUrl=config.SQS_QUEUE_URL,
        MaxNumberOfMessages=max_messages,
        WaitTimeSeconds=10
    )
    return response.get("Messages", [])

def delete_message(receipt_handle):
    logger.log(f"Deleting message with ReceiptHandle: {receipt_handle}")
    sqs.delete_message(
        QueueUrl=config.SQS_QUEUE_URL,
        ReceiptHandle=receipt_handle
    )

