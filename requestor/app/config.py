"""Configuration settings for requestor service."""
import os
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

class Settings:
    """Application settings loaded from environment variables."""
    AWS_REGION: str = os.getenv("AWS_REGION", "us-east-1")
    SQS_QUEUE_URL: Optional[str] = os.getenv("SQS_QUEUE_URL")
    
    def __post_init__(self) -> None:
        """Validate required environment variables."""
        if not self.SQS_QUEUE_URL:
            raise ValueError("SQS_QUEUE_URL environment variable is required")

settings = Settings()
settings.__post_init__()
