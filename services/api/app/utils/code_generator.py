import string
import secrets
from app.utils.logger import logger

BASE62_CHARS = string.digits + string.ascii_uppercase + string.ascii_lowercase

def generate_short_code(length: int = 6) -> str:
    code = ''.join(secrets.choice(BASE62_CHARS) for _ in range(length))
    logger.info(f"Generated short code of length {length}")
    return code

def is_valid_short_code(code: str) -> bool:
    if not code or len(code) < 3 or len(code) > 20:
        logger.warning(f"Invalid short code length: {len(code) if code else 0}")
        return False
    is_valid = all(c in BASE62_CHARS for c in code)
    if not is_valid:
        logger.warning(f"Short code contains invalid characters: {code}")
    return is_valid