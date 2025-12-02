import boto3
from typing import List, Dict, Any
from . import config

ses = boto3.client("ses", region_name=config.AWS_REGION)
sns = boto3.client("sns", region_name=config.AWS_REGION)

def send_email(domain_arn: str, to_addresses: List[str], subject: str, body: str) -> Dict[str, Any]:
    """Send email notification via Amazon SES."""
    if not to_addresses or not isinstance(to_addresses, list):
        raise ValueError("to_addresses must be a non-empty list")
    if not subject or not isinstance(subject, str):
        raise ValueError("subject must be a non-empty string")
    if not body or not isinstance(body, str):
        raise ValueError("body must be a non-empty string")
    
    try:
        sender_email = "notifications@project-dolphin.com"
        return ses.send_email(
            Source=sender_email,
            Destination={"ToAddresses": to_addresses},
            Message={
                "Subject": {"Data": subject},
                "Body": {"Text": {"Data": body}}
            }
        )
    except Exception as e:
        raise RuntimeError(f"Failed to send email: {str(e)}")

def send_sns(topic_arn: str, message: str) -> Dict[str, Any]:
    """Send SNS notification to topic."""
    if not topic_arn or not isinstance(topic_arn, str):
        raise ValueError("topic_arn must be a non-empty string")
    if not message or not isinstance(message, str):
        raise ValueError("message must be a non-empty string")
    
    try:
        return sns.publish(TopicArn=topic_arn, Message=message)
    except Exception as e:
        raise RuntimeError(f"Failed to send SNS message: {str(e)}")

