# auracrypt2/utils/helpers.py
"""
General utility functions used throughout the application.
"""

import re
import random
import string
import urllib.parse
from datetime import datetime, timedelta
from typing import Optional, Tuple
from core.constants import AppConstants


def format_time_ago(timestamp: str) -> str:
    """
    Format timestamp to human readable time ago.

    Args:
        timestamp: ISO format timestamp string

    Returns:
        Human readable time ago string (e.g., "2 hours ago", "3 days ago")
    """
    try:
        dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
        now = datetime.now()
        diff = now - dt

        if diff.days > 0:
            if diff.days == 1:
                return "1 day ago"
            elif diff.days < 7:
                return f"{diff.days} days ago"
            elif diff.days < 30:
                weeks = diff.days // 7
                return f"{weeks} week{'s' if weeks > 1 else ''} ago"
            elif diff.days < 365:
                months = diff.days // 30
                return f"{months} month{'s' if months > 1 else ''} ago"
            else:
                years = diff.days // 365
                return f"{years} year{'s' if years > 1 else ''} ago"

        seconds = diff.seconds
        if seconds < 60:
            return "Just now"
        elif seconds < 3600:
            minutes = seconds // 60
            return f"{minutes} minute{'s' if minutes > 1 else ''} ago"
        else:
            hours = seconds // 3600
            return f"{hours} hour{'s' if hours > 1 else ''} ago"

    except (ValueError, AttributeError):
        return "Unknown"


def validate_url(url: str) -> Tuple[bool, str]:
    """
    Validate URL format and return cleaned URL.

    Args:
        url: URL string to validate

    Returns:
        Tuple of (is_valid, cleaned_url)
    """
    if not url or not url.strip():
        return True, ""  # Empty URL is valid (optional field)

    url = url.strip()

    # Add protocol if missing
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url

    try:
        parsed = urllib.parse.urlparse(url)

        # Check if domain exists
        if not parsed.netloc:
            return False, url

        # Basic domain validation
        domain_pattern = re.compile(
            r'^[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?(\.[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?)*$'
        )

        if not domain_pattern.match(parsed.netloc.split(':')[0]):
            return False, url

        return True, url

    except Exception:
        return False, url


def generate_secure_password(
    length: int = AppConstants.PASSWORD_GENERATOR_DEFAULT_LENGTH,
    use_uppercase: bool = True,
    use_lowercase: bool = True,
    use_numbers: bool = True,
    use_symbols: bool = True
) -> str:
    """
    Generate a secure password with specified criteria.

    Args:
        length: Password length (minimum 8)
        use_uppercase: Include uppercase letters
        use_lowercase: Include lowercase letters
        use_numbers: Include numbers
        use_symbols: Include special symbols

    Returns:
        Generated password string
    """
    if length < AppConstants.MIN_PASSWORD_LENGTH:
        length = AppConstants.MIN_PASSWORD_LENGTH

    # Character sets
    chars = ""
    guaranteed_chars = []

    if use_uppercase:
        chars += string.ascii_uppercase
        guaranteed_chars.append(random.choice(string.ascii_uppercase))

    if use_lowercase:
        chars += string.ascii_lowercase
        guaranteed_chars.append(random.choice(string.ascii_lowercase))

    if use_numbers:
        chars += string.digits
        guaranteed_chars.append(random.choice(string.digits))

    if use_symbols:
        symbols = "!@#$%^&*()_+-=[]{}|;':,./<>?"
        chars += symbols
        guaranteed_chars.append(random.choice(symbols))

    if not chars:
        # Fallback if no character sets selected
        chars = string.ascii_letters + string.digits
        guaranteed_chars = [
            random.choice(string.ascii_uppercase),
            random.choice(string.ascii_lowercase),
            random.choice(string.digits)
        ]

    # Generate remaining characters
    remaining_length = length - len(guaranteed_chars)
    random_chars = [random.choice(chars) for _ in range(remaining_length)]

    # Combine and shuffle
    password_chars = guaranteed_chars + random_chars
    random.shuffle(password_chars)

    return ''.join(password_chars)


def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename by removing invalid characters.

    Args:
        filename: Original filename

    Returns:
        Sanitized filename safe for filesystem
    """
    # Remove invalid characters for Windows/Unix
    invalid_chars = r'[<>:"/\\|?*]'
    sanitized = re.sub(invalid_chars, '_', filename)

    # Remove control characters
    sanitized = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', sanitized)

    # Trim whitespace and dots
    sanitized = sanitized.strip(' .')

    # Ensure not empty
    if not sanitized:
        sanitized = "untitled"

    return sanitized


def get_current_timestamp() -> str:
    """
    Get current timestamp in ISO format.

    Returns:
        Current timestamp as ISO string
    """
    return datetime.now().isoformat()


def is_strong_password(password: str) -> Tuple[bool, list[str]]:
    """
    Check if password meets strength requirements.

    Args:
        password: Password to check

    Returns:
        Tuple of (is_strong, list_of_issues)
    """
    issues = []

    if len(password) < AppConstants.MIN_PASSWORD_LENGTH:
        issues.append(f"Must be at least {AppConstants.MIN_PASSWORD_LENGTH} characters long")

    if not re.search(r'[a-z]', password):
        issues.append("Must contain lowercase letters")

    if not re.search(r'[A-Z]', password):
        issues.append("Must contain uppercase letters")

    if not re.search(r'\d', password):
        issues.append("Must contain numbers")

    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        issues.append("Must contain special characters")

    # Check for common weak patterns
    if re.search(r'(.)\1{2,}', password):  # Three or more repeated characters
        issues.append("Avoid repeated characters")

    if re.search(r'(012|123|234|345|456|567|678|789|890|abc|bcd|cde)', password.lower()):
        issues.append("Avoid sequential characters")

    return len(issues) == 0, issues


def truncate_text(text: str, max_length: int, suffix: str = "...") -> str:
    """
    Truncate text to specified length with suffix.

    Args:
        text: Text to truncate
        max_length: Maximum length including suffix
        suffix: Suffix to add when truncated

    Returns:
        Truncated text
    """
    if not text or len(text) <= max_length:
        return text

    return text[:max_length - len(suffix)] + suffix


def extract_domain_from_url(url: str) -> Optional[str]:
    """
    Extract domain name from URL.

    Args:
        url: URL string

    Returns:
        Domain name or None if invalid
    """
    try:
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url

        parsed = urllib.parse.urlparse(url)
        domain = parsed.netloc.lower()

        # Remove www. prefix
        if domain.startswith('www.'):
            domain = domain[4:]

        return domain if domain else None

    except Exception:
        return None
