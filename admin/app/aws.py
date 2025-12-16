"""AWS service setup operations for admin service."""
import boto3
from typing import Dict, Any, List
from .config import settings

def setup_app_services(app: Any) -> Dict[str, Any]:
    """Set up AWS services (SES, SNS) for an application."""
    try:
        ses = boto3.client(
            "ses",
            region_name=settings.AWS_REGION
        )
        sns = boto3.client(
            "sns",
            region_name=settings.AWS_REGION
        )
    except Exception as e:
        raise RuntimeError(f"Failed to create AWS clients: {str(e)}")

    try:
        domain = app.Domain

        # Verify domain for SES
        verify_response = ses.verify_domain_identity(Domain=domain)
        verification_token = verify_response["VerificationToken"]

        # Enable DKIM
        dkim_response = ses.verify_domain_dkim(Domain=domain)
        dkim_tokens = dkim_response["DkimTokens"]

        # Create SNS topic
        sns_response = sns.create_topic(Name=app.Application)
        sns_arn = sns_response["TopicArn"]

        ses_arn = f"arn:aws:ses:{settings.AWS_REGION}:{settings.AWS_ACCOUNT_ID}:identity/{domain}"
    except Exception as e:
        raise RuntimeError(f"Failed to setup AWS services: {str(e)}")

    return {
        "App name": app.App_name,
        "Application": app.Application,
        "Email": app.Email,
        "Domain": domain,
        "SES-Domain-ARN": ses_arn,
        "SES-Verification-TXT": {
            "Name": f"_amazonses.{domain}",
            "Type": "TXT",
            "Value": verification_token
        },
        "DKIM-Records": [
            {
                "Name": f"{token}._domainkey.{domain}",
                "Type": "CNAME",
                "Value": f"{token}.dkim.amazonses.com"
            } for token in dkim_tokens
        ],
        "SNS-Topic-ARN": sns_arn
    }

