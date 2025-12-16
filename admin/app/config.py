"""Configuration settings for admin service."""
import os
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

class Settings:
    """Application settings loaded from environment variables."""
    AWS_REGION: str = os.getenv("AWS_REGION", "us-east-1")
    AWS_ACCESS_KEY_ID: Optional[str] = os.getenv("AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY: Optional[str] = os.getenv("AWS_SECRET_ACCESS_KEY")
    AWS_ACCOUNT_ID: Optional[str] = os.getenv("AWS_ACCOUNT_ID")
    APP_CONFIG_TABLE: str = os.getenv("APPLICATIONS_TABLE", "Applications")
    API_KEYS_TABLE: str = os.getenv("API_KEYS_TABLE", "YANTECH-YNP01-AWS-DYNAMODB-API-KEYS-DEV")

settings = Settings()

