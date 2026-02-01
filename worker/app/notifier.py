import boto3
from typing import List, Dict, Any
from datetime import datetime
from . import config, logger

# CRITICAL: This code uses boto3.client("ses") which requires:
# VPC Endpoint: com.amazonaws.us-east-1.email (API endpoint)
# NOT: com.amazonaws.us-east-1.email-smtp (SMTP endpoint)
ses = boto3.client("ses", region_name=config.AWS_REGION)
sns = boto3.client("sns", region_name=config.AWS_REGION)

def send_email(domain_arn: str, to_addresses: List[str], subject: str, body: str) -> Dict[str, Any]:
    """Send email notification via Amazon SES with YANTECH branded template."""
    if not to_addresses or not isinstance(to_addresses, list):
        raise ValueError("to_addresses must be a non-empty list")
    if not subject or not isinstance(subject, str):
        raise ValueError("subject must be a non-empty string")
    if not body or not isinstance(body, str):
        raise ValueError("body must be a non-empty string")
    
    sender_email = "notifications@project-dolphin.com"
    logger.log(f"[SES] Sending email from {sender_email} to {to_addresses}")
    
    try:
        # YANTECH branded HTML template
        html_body = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>YANTECH Notification</title>
</head>
<body style="margin: 0; padding: 0; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f5f5f5;">
    <table role="presentation" style="width: 100%; border-collapse: collapse;">
        <tr>
            <td style="padding: 40px 20px;">
                <table role="presentation" style="max-width: 600px; margin: 0 auto; background-color: white; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
                    <tr>
                        <td style="padding: 40px;">
                            <div style="text-align: center; margin-bottom: 30px;">
                                <h1 style="color: #2c5aa0; margin: 0; font-size: 28px;">YANTECH</h1>
                                <p style="color: #666; margin: 5px 0 0 0; font-size: 14px;">Notification Platform</p>
                            </div>
                            
                            <h2 style="color: #333; margin: 0 0 20px 0; font-size: 20px;">{subject}</h2>
                            
                            <p style="color: #555; line-height: 1.6; margin: 0 0 15px 0;">
                                Hello,
                            </p>
                            
                            <div style="background-color: #f8f9fa; padding: 20px; border-radius: 6px; margin: 20px 0;">
                                <div style="color: #555; line-height: 1.6;">
                                    {body.replace(chr(10), '<br>')}
                                </div>
                            </div>
                            
                            <div style="background-color: #f0f8ff; padding: 15px; border-radius: 6px; margin: 20px 0; border-left: 4px solid #2c5aa0;">
                                <h3 style="color: #2c5aa0; margin: 0 0 10px 0; font-size: 14px;">Message Details:</h3>
                                <ul style="color: #666; margin: 0; padding-left: 20px; font-size: 12px;">
                                    <li>Sender: YANTECH Notification System</li>
                                    <li>Time: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}</li>
                                </ul>
                            </div>
                            
                            <p style="color: #555; line-height: 1.6; margin: 0 0 15px 0;">
                                If you have any questions, please contact our support team.
                            </p>
                            
                            <p style="color: #555; line-height: 1.6; margin: 0 0 30px 0;">
                                Best regards,<br>
                                <strong>YANTECH Team</strong>
                            </p>
                            
                            <hr style="border: none; border-top: 1px solid #eee; margin: 30px 0;">
                            
                            <div style="text-align: center;">
                                <p style="color: #999; font-size: 12px; margin: 0;">
                                    YANTECH Notification Platform<br>
                                    <a href="https://project-panther.com" style="color: #2c5aa0; text-decoration: none;">https://project-panther.com</a>
                                </p>
                            </div>
                        </td>
                    </tr>
                </table>
            </td>
        </tr>
    </table>
</body>
</html>
        """
        
        # Text version for email clients that don't support HTML
        text_body = f"""
Hello,

{body}

Message Details:
- Sender: YANTECH Notification System
- Time: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}

If you have any questions, please contact our support team.

Best regards,
YANTECH Team

---
YANTECH Notification Platform
https://project-panther.com
        """.strip()
        
        response = ses.send_email(
            Source=sender_email,
            Destination={"ToAddresses": to_addresses},
            Message={
                "Subject": {"Data": subject, "Charset": "UTF-8"},
                "Body": {
                    "Text": {"Data": text_body, "Charset": "UTF-8"},
                    "Html": {"Data": html_body, "Charset": "UTF-8"}
                }
            },
            ReturnPath=sender_email,
            ReplyToAddresses=["support@project-dolphin.com"],
            Tags=[
                {"Name": "Environment", "Value": "production"},
                {"Name": "Service", "Value": "notification-worker"},
                {"Name": "MessageType", "Value": "notification"}
            ]
        )
        logger.log(f"[SES] Email sent successfully: {response.get('MessageId')}")
        return response
    except Exception as e:
        logger.log(f"[SES] Email send failed: {str(e)}")
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

