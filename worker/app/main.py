"""Main worker process for handling SQS messages."""
import json
import time
from typing import Dict, Any, List
from . import sqs_client, dynamodb_client, notifier, logger
from .health import health_checker


def _process_message(msg: Dict[str, Any]) -> bool:
    """Process a single SQS message. Returns True if successful, False otherwise."""
    body = None
    try:
        body = json.loads(msg["Body"])
        app_id = body["Application"]
        logger.log(f"Processing message for application: {app_id}")
        cfg = dynamodb_client.get_application_config(app_id)
        if not cfg:
            raise ValueError("App config not found")

        output = body.get("OutputType", "").upper()  # Convert to uppercase
        if output == "EMAIL":
            # Use Recipient field if EmailAddresses is not available or null
            email_addresses = body.get("EmailAddresses")
            if not email_addresses or email_addresses == [None] or email_addresses == [""]:
                email_addresses = [body.get("Recipient")]
            if isinstance(email_addresses, str):
                email_addresses = [email_addresses]
            # Filter out None/empty values
            email_addresses = [email for email in email_addresses if email]
            
            # Use default SES domain ARN if not configured
            ses_domain = cfg.get("SES-Domain-ARN", "arn:aws:ses:us-east-1:588082972397:identity/project-dolphin.com")
            notifier.send_email(ses_domain, email_addresses, body["Subject"], body["Message"])
            logger.log(f"Email sent to {email_addresses}")
        elif output in ["SMS", "PUSH"]:
            # Use default SNS topic ARN if not configured
            sns_topic = cfg.get("SNS-Topic-ARN", "arn:aws:sns:us-east-1:588082972397:YANTECH-push-notifications-dev")
            notifier.send_sns(sns_topic, body["Message"])
            logger.log(f"Notification sent via {output} to {body.get('PhoneNumber') or body.get('PushToken')}")
        else:
            raise ValueError(f"Unsupported OutputType: {output}")

        dynamodb_client.log_request(app_id, body, "delivered")
        logger.log(f"Message processed successfully: {body}")
        health_checker.record_message_processed()
        return True
    except Exception as e:
        # Log the error
        dynamodb_client.log_request(body.get("Application", "unknown") if body else "unknown", body, "failed", str(e))
        logger.log(f"Error processing message: {e}")
        health_checker.record_error()
        # Don't delete the message - let it retry or go to DLQ
        logger.log(f"Message will be retried or sent to DLQ after max attempts")
        return False


def run_worker() -> None:
    """Main worker loop for processing SQS messages."""
    logger.log("Worker started polling SQS...")
    backoff_delay = 1  # Initial backoff delay in seconds
    max_backoff = 60   # Maximum backoff delay in seconds
    
    while True:
        try:
            messages = sqs_client.poll_messages()
            # Reset backoff delay after successful API call
            backoff_delay = 1
        except Exception as e:
            logger.log(f"Error polling SQS: {e}")
            logger.log(f"Backing off for {backoff_delay} seconds")
            health_checker.record_error()
            time.sleep(backoff_delay)
            # Double the backoff delay for next attempt, up to maximum
            backoff_delay = min(backoff_delay * 2, max_backoff)
            continue
        
        if not messages:
            time.sleep(1)  # Short sleep when no messages
            continue
            
        for msg in messages:
            if _process_message(msg):
                # Only delete message if processing was successful
                sqs_client.delete_message(msg["ReceiptHandle"])
                logger.log("Message deleted from SQS")

if __name__ == "__main__":
    run_worker()

