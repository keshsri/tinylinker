import hashlib
import os
from datetime import datetime

def hash_string(input_str: str) -> str:
    return hashlib.sha256(input_str.encode()).hexdigest()

def hash_ip(ip: str) -> str:
    date = datetime.utcnow().strftime('%Y-%m-%d')
    salt = os.environ.get('IP_SALT_SECRET', 'default-salt')
    return hash_string(f"{ip}{date}{salt}")