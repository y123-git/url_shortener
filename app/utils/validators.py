"""
URL Validators
"""

import re
from urllib.parse import urlparse
from typing import Optional

def validate_url(url: str) -> bool:
    """Validate URL format."""
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except:
        return False

def normalize_url(url: str) -> str:
    """Normalize URL."""
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    return url.rstrip('/')

def extract_domain(url: str) -> Optional[str]:
    """Extract domain from URL."""
    try:
        parsed = urlparse(url)
        return parsed.netloc
    except:
        return None

def is_blocked_domain(url: str) -> bool:
    """Check if domain is blocked."""
    blocked_domains = [
        'localhost',
        '127.0.0.1',
        '0.0.0.0',
        'internal',
    ]
    domain = extract_domain(url)
    return domain in blocked_domains if domain else False

def validate_custom_code(code: str) -> bool:
    """Validate custom code format."""
    pattern = r'^[a-zA-Z0-9_-]{3,10}$'
    return bool(re.match(pattern, code))