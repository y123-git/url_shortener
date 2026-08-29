"""
URL Shortening Utilities
"""

import hashlib
import random
import string
from typing import Optional
from datetime import datetime

class URLShortener:
    """URL shortening utilities."""
    
    CHARS = string.ascii_letters + string.digits
    BASE = len(CHARS)
    
    @classmethod
    def generate_code_md5(cls, url: str, length: int = 6) -> str:
        """Generate short code using MD5 hash."""
        return hashlib.md5(url.encode()).hexdigest()[:length]
    
    @classmethod
    def generate_code_base62(cls, num: int) -> str:
        """Convert number to Base62 string."""
        if num == 0:
            return cls.CHARS[0]
        
        result = []
        while num > 0:
            result.append(cls.CHARS[num % cls.BASE])
            num //= cls.BASE
        
        return ''.join(reversed(result))
    
    @classmethod
    def generate_random_code(cls, length: int = 6) -> str:
        """Generate random short code."""
        return ''.join(random.choices(cls.CHARS, k=length))
    
    @classmethod
    def generate_code_with_salt(cls, url: str, salt: str = "") -> str:
        """Generate code with salt for collision avoidance."""
        combined = url + salt
        return cls.generate_code_md5(combined)
    
    @classmethod
    def generate_unique_code(cls, db, url: str, max_attempts: int = 10) -> str:
        """Generate unique short code with collision handling."""
        from app.crud import URLCRUD
        
        # Try MD5 first
        code = cls.generate_code_md5(url)
        if not URLCRUD.exists(db, code):
            return code
        
        # Try with random suffix
        for i in range(max_attempts):
            salt = ''.join(random.choices(cls.CHARS, k=2))
            code = cls.generate_code_with_salt(url, salt)
            if not URLCRUD.exists(db, code):
                return code
        
        # Final attempt with timestamp
        timestamp = str(datetime.utcnow().timestamp()).replace('.', '')[-6:]
        code = cls.generate_code_with_salt(url, timestamp)
        if not URLCRUD.exists(db, code):
            return code
        
        # Try random generation
        for i in range(max_attempts):
            code = cls.generate_random_code(8)
            if not URLCRUD.exists(db, code):
                return code
        
        raise RuntimeError("Could not generate unique short code")