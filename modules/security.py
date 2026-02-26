"""
PERSEPTOR v2.0 - Security Hardening Module
Input validation, output sanitization, SSRF prevention, rate limiting helpers.
"""

import re
import html
import ipaddress
import socket
from urllib.parse import urlparse
from typing import Optional, Tuple
from modules.logging_config import get_logger

logger = get_logger("security")

# ─── Input Validation ─────────────────────────────────────────────────────────

# Maximum sizes for various inputs
MAX_URL_LENGTH = 2048
MAX_TEXT_LENGTH = 500_000  # 500KB of text
MAX_PROMPT_LENGTH = 10_000
MAX_API_KEY_LENGTH = 256

# Allowed URL schemes
ALLOWED_SCHEMES = {"http", "https"}

# Blocked IP ranges (private, loopback, link-local)
BLOCKED_NETWORKS = [
    ipaddress.ip_network("10.0.0.0/8"),
    ipaddress.ip_network("172.16.0.0/12"),
    ipaddress.ip_network("192.168.0.0/16"),
    ipaddress.ip_network("127.0.0.0/8"),
    ipaddress.ip_network("169.254.0.0/16"),
    ipaddress.ip_network("0.0.0.0/8"),
    ipaddress.ip_network("::1/128"),
    ipaddress.ip_network("fc00::/7"),
    ipaddress.ip_network("fe80::/10"),
]

# Dangerous characters/patterns in user input
DANGEROUS_PATTERNS = [
    re.compile(r'<script', re.IGNORECASE),
    re.compile(r'javascript:', re.IGNORECASE),
    re.compile(r'on\w+\s*=', re.IGNORECASE),
    re.compile(r'data:\s*text/html', re.IGNORECASE),
    re.compile(r'vbscript:', re.IGNORECASE),
]


def validate_url(url: str) -> Tuple[bool, str]:
    """
    Validate a URL for safety. Returns (is_valid, error_message).
    Checks: length, scheme, SSRF (private IPs), DNS resolution.
    """
    if not url or not isinstance(url, str):
        return False, "URL is required"

    url = url.strip()

    if len(url) > MAX_URL_LENGTH:
        return False, f"URL exceeds maximum length of {MAX_URL_LENGTH} characters"

    try:
        parsed = urlparse(url)
    except Exception:
        return False, "Invalid URL format"

    if not parsed.scheme:
        return False, "URL must include a scheme (http:// or https://)"

    if parsed.scheme.lower() not in ALLOWED_SCHEMES:
        return False, f"URL scheme '{parsed.scheme}' is not allowed. Use http or https"

    if not parsed.hostname:
        return False, "URL must include a hostname"

    hostname = parsed.hostname

    # Check for IP address in URL (potential SSRF)
    try:
        ip = ipaddress.ip_address(hostname)
        for network in BLOCKED_NETWORKS:
            if ip in network:
                logger.warning(f"SSRF attempt blocked: {url} resolves to private IP {ip}")
                return False, "URL points to a restricted network address"
    except ValueError:
        # Not an IP, it's a hostname - resolve it
        try:
            resolved_ips = socket.getaddrinfo(hostname, None, socket.AF_UNSPEC, socket.SOCK_STREAM)
            for family, _, _, _, sockaddr in resolved_ips:
                ip_str = sockaddr[0]
                try:
                    ip = ipaddress.ip_address(ip_str)
                    for network in BLOCKED_NETWORKS:
                        if ip in network:
                            logger.warning(
                                f"SSRF attempt blocked: {hostname} resolves to private IP {ip}"
                            )
                            return False, "URL hostname resolves to a restricted network address"
                except ValueError:
                    continue
        except socket.gaierror:
            return False, f"Cannot resolve hostname: {hostname}"

    return True, ""


def validate_api_key(api_key: str) -> Tuple[bool, str]:
    """Validate API key format."""
    if not api_key or not isinstance(api_key, str):
        return False, "API key is required"

    api_key = api_key.strip()

    if len(api_key) > MAX_API_KEY_LENGTH:
        return False, "API key exceeds maximum length"

    if len(api_key) < 10:
        return False, "API key is too short"

    # Check for common invalid patterns
    if any(p.search(api_key) for p in DANGEROUS_PATTERNS):
        logger.warning("Dangerous pattern detected in API key input")
        return False, "Invalid API key format"

    return True, ""


def validate_prompt(prompt: str) -> Tuple[bool, str]:
    """Validate prompt input."""
    if not prompt or not isinstance(prompt, str):
        return False, "Prompt is required"

    prompt = prompt.strip()

    if len(prompt) > MAX_PROMPT_LENGTH:
        return False, f"Prompt exceeds maximum length of {MAX_PROMPT_LENGTH} characters"

    if len(prompt) < 5:
        return False, "Prompt is too short"

    return True, ""


def validate_text_input(text: str, field_name: str = "input") -> Tuple[bool, str]:
    """Validate generic text input."""
    if not isinstance(text, str):
        return False, f"{field_name} must be a string"

    if len(text) > MAX_TEXT_LENGTH:
        return False, f"{field_name} exceeds maximum length of {MAX_TEXT_LENGTH} characters"

    return True, ""


# ─── Output Sanitization ─────────────────────────────────────────────────────

def sanitize_html(text: str) -> str:
    """Sanitize text to prevent XSS in HTML context."""
    if not isinstance(text, str):
        return str(text)
    return html.escape(text, quote=True)


def sanitize_for_json(obj):
    """Recursively sanitize an object for safe JSON output."""
    if isinstance(obj, str):
        # Remove null bytes and control characters
        cleaned = obj.replace('\x00', '')
        cleaned = re.sub(r'[\x01-\x08\x0b\x0c\x0e-\x1f\x7f]', '', cleaned)
        return cleaned
    elif isinstance(obj, dict):
        return {sanitize_for_json(k): sanitize_for_json(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [sanitize_for_json(item) for item in obj]
    elif isinstance(obj, (int, float, bool, type(None))):
        return obj
    else:
        return str(obj)


def sanitize_filename(filename: str) -> str:
    """Sanitize a filename to prevent path traversal."""
    # Remove path separators and null bytes
    sanitized = re.sub(r'[/\\:\x00]', '', filename)
    # Remove leading dots (prevent hidden files)
    sanitized = sanitized.lstrip('.')
    # Limit length
    sanitized = sanitized[:255]
    return sanitized or "unnamed"


# ─── Request Validation ──────────────────────────────────────────────────────

def validate_content_type(content_type: Optional[str], expected: str = "application/json") -> bool:
    """Validate that the Content-Type header matches expected type."""
    if not content_type:
        return False
    return expected.lower() in content_type.lower()


def check_request_size(content_length: Optional[int], max_size: int = 10 * 1024 * 1024) -> Tuple[bool, str]:
    """Check if request body size is within limits (default 10MB)."""
    if content_length is None:
        return True, ""
    if content_length > max_size:
        return False, f"Request body exceeds maximum size of {max_size // 1024 // 1024}MB"
    return True, ""


# ─── Security Headers ────────────────────────────────────────────────────────

SECURITY_HEADERS = {
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
    "X-XSS-Protection": "1; mode=block",
    "Referrer-Policy": "strict-origin-when-cross-origin",
    "Cache-Control": "no-store, no-cache, must-revalidate, max-age=0",
    "Pragma": "no-cache",
}


def apply_security_headers(response):
    """Apply security headers to a Flask response object."""
    for header, value in SECURITY_HEADERS.items():
        response.headers[header] = value
    return response
