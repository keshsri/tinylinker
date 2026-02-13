import string
import secrets

BASE62_CHARS = string.digits + string.ascii_uppercase + string.ascii_lowercase

def generate_short_code(length: int = 6) -> str:
    return ''.join(secrets.choice(BASE62_CHARS) for _ in range(length))

def is_valid_short_code(code: str) -> bool:
    if not code or len(code) < 3 or len(code) > 20:
        return False
    return all(c in BASE62_CHARS for c in code)