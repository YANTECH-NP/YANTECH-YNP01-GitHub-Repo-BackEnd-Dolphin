"""Simple logging utility for worker service."""
import sys
import logging
from typing import Any

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def log(msg: Any) -> None:
    """Log message to stdout and logger."""
    message = f"[✓] {msg}"
    sys.stdout.write(f"{message}\n")
    sys.stdout.flush()
    logger.info(msg)

