"""Simple health check for worker service."""
from datetime import datetime, timezone
from typing import Dict, Any, Optional

class HealthChecker:
    """Health checker for monitoring worker service status."""
    def __init__(self) -> None:
        self.start_time = datetime.now(timezone.utc)
        self.last_message_processed: Optional[datetime] = None
        self.messages_processed = 0
        self.errors_count = 0
        self.dlq_messages_count = 0
    
    def record_message_processed(self) -> None:
        self.last_message_processed = datetime.now(timezone.utc)
        self.messages_processed += 1
    
    def record_error(self) -> None:
        self.errors_count += 1
    
    def record_dlq_message(self) -> None:
        self.dlq_messages_count += 1
    
    def get_status(self) -> Dict[str, Any]:
        uptime = (datetime.now(timezone.utc) - self.start_time).total_seconds()
        return {
            "status": "healthy",
            "uptime_seconds": uptime,
            "messages_processed": self.messages_processed,
            "errors_count": self.errors_count,
            "dlq_messages_count": self.dlq_messages_count,
            "last_message_processed": self.last_message_processed.isoformat() if self.last_message_processed else None,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

# Global health checker instance
health_checker = HealthChecker()