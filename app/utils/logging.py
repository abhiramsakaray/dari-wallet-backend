import logging
import os
from datetime import datetime
from app.core.config import settings


def setup_logging():
    """Setup logging configuration"""
    # Create logs directory if it doesn't exist
    os.makedirs("logs", exist_ok=True)
    
    # Configure logging
    logging.basicConfig(
        level=getattr(logging, settings.log_level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(settings.log_file),
            logging.StreamHandler()
        ]
    )


def log_user_activity(user_id: int, action: str, details: dict = None, level: str = "INFO"):
    """Log user activity"""
    logger = logging.getLogger("user_activity")
    log_data = {
        "user_id": user_id,
        "action": action,
        "details": details,
        "timestamp": datetime.utcnow().isoformat()
    }
    
    if level.upper() == "INFO":
        logger.info(f"User activity: {log_data}")
    elif level.upper() == "WARNING":
        logger.warning(f"User activity: {log_data}")
    elif level.upper() == "ERROR":
        logger.error(f"User activity: {log_data}")


def log_system_event(event: str, details: dict = None, level: str = "INFO"):
    """Log system events"""
    logger = logging.getLogger("system")
    log_data = {
        "event": event,
        "details": details,
        "timestamp": datetime.utcnow().isoformat()
    }
    
    if level.upper() == "INFO":
        logger.info(f"System event: {log_data}")
    elif level.upper() == "WARNING":
        logger.warning(f"System event: {log_data}")
    elif level.upper() == "ERROR":
        logger.error(f"System event: {log_data}")


def log_transaction(tx_hash: str, chain: str, status: str, details: dict = None):
    """Log transaction events"""
    logger = logging.getLogger("transactions")
    log_data = {
        "tx_hash": tx_hash,
        "chain": chain,
        "status": status,
        "details": details,
        "timestamp": datetime.utcnow().isoformat()
    }
    
    logger.info(f"Transaction: {log_data}")


def log_admin_action(admin_id: int, action: str, details: dict = None):
    """Log admin actions"""
    logger = logging.getLogger("admin")
    log_data = {
        "admin_id": admin_id,
        "action": action,
        "details": details,
        "timestamp": datetime.utcnow().isoformat()
    }
    
    logger.info(f"Admin action: {log_data}") 