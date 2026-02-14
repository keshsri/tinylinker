import hashlib
import os
from datetime import datetime
from app.utils.logger import logger

def hash_string(input_str: str) -> str:
    hashed = hashlib.sha256(input_str.encode()).hexdigest()
    logger.info("String hashed successfully")
    return hashed

def hash_ip(ip: str) -> str:
    date = datetime.utcnow().strftime('%Y-%m-%d')
    salt = os.environ.get('IP_SALT_SECRET', 'default-salt')
    hashed = hash_string(f"{ip}{date}{salt}")
    logger.info(f"IP hashed for date: {date}")
    return hashed