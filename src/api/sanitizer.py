"""
Input Validation and Sanitization
Prevents XSS, SQL Injection, and other security vulnerabilities
"""

import re
import html
from typing import Any, Dict, Optional
from fastapi import HTTPException


class InputSanitizer:
    """Sanitize and validate user inputs"""

    # Dangerous patterns to detect
    XSS_PATTERNS = [
        r'<script[^>]*>.*?</script>',
        r'javascript:',
        r'on\w+\s*=',
        r'<iframe',
        r'<object',
        r'<embed',
        r'<applet',
    ]

    SQL_INJECTION_PATTERNS = [
        r"(\b(SELECT|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER|EXEC|EXECUTE)\b)",
        r"(--|;|\/\*|\*\/)",
        r"(\bOR\b.*=.*)",
        r"(\bAND\b.*=.*)",
        r"('|\"|`)",
    ]

    @staticmethod
    def sanitize_html(text: str) -> str:
        """
        Escape HTML special characters to prevent XSS
        """
        if not text:
            return text
        return html.escape(text)

    @staticmethod
    def detect_xss(text: str) -> bool:
        """
        Detect potential XSS attacks
        """
        if not text:
            return False

        text_lower = text.lower()
        for pattern in InputSanitizer.XSS_PATTERNS:
            if re.search(pattern, text_lower, re.IGNORECASE):
                return True
        return False

    @staticmethod
    def detect_sql_injection(text: str) -> bool:
        """
        Detect potential SQL injection attempts
        """
        if not text:
            return False

        for pattern in InputSanitizer.SQL_INJECTION_PATTERNS:
            if re.search(pattern, text, re.IGNORECASE):
                return True
        return False

    @staticmethod
    def sanitize_string(
        text: str,
        max_length: Optional[int] = None,
        allow_html: bool = False,
        field_name: str = "input"
    ) -> str:
        """
        Sanitize a string input

        Args:
            text: Input text to sanitize
            max_length: Maximum allowed length
            allow_html: Whether to allow HTML (default: False)
            field_name: Name of the field for error messages

        Returns:
            Sanitized string

        Raises:
            HTTPException: If input contains malicious content
        """
        if not text:
            return text

        # Check for XSS
        if InputSanitizer.detect_xss(text):
            raise HTTPException(
                status_code=400,
                detail=f"Invalid {field_name}: potentially malicious content detected"
            )

        # Check for SQL injection
        if InputSanitizer.detect_sql_injection(text):
            raise HTTPException(
                status_code=400,
                detail=f"Invalid {field_name}: potentially malicious content detected"
            )

        # Escape HTML if not allowed
        if not allow_html:
            text = InputSanitizer.sanitize_html(text)

        # Trim whitespace
        text = text.strip()

        # Check length
        if max_length and len(text) > max_length:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid {field_name}: maximum length is {max_length} characters"
            )

        return text

    @staticmethod
    def sanitize_email(email: str) -> str:
        """
        Validate and sanitize email address
        """
        if not email:
            raise HTTPException(status_code=400, detail="Email is required")

        email = email.strip().lower()

        # Basic email regex
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, email):
            raise HTTPException(status_code=400, detail="Invalid email format")

        if len(email) > 254:  # RFC 5321
            raise HTTPException(status_code=400, detail="Email too long")

        return email

    @staticmethod
    def sanitize_phone(phone: str) -> str:
        """
        Validate and sanitize phone number
        """
        if not phone:
            raise HTTPException(status_code=400, detail="Phone number is required")

        # Remove all non-digit characters except +
        phone = re.sub(r'[^\d+]', '', phone)

        # Check format
        if not re.match(r'^\+?[1-9]\d{1,14}$', phone):
            raise HTTPException(
                status_code=400,
                detail="Invalid phone number format. Use international format: +1234567890"
            )

        return phone

    @staticmethod
    def sanitize_dict(
        data: Dict[str, Any],
        field_rules: Dict[str, Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Sanitize a dictionary of inputs based on field rules

        Args:
            data: Input dictionary
            field_rules: Rules for each field
                {
                    "field_name": {
                        "type": "string|email|phone",
                        "required": True|False,
                        "max_length": int,
                        "allow_html": True|False
                    }
                }

        Returns:
            Sanitized dictionary
        """
        sanitized = {}

        for field_name, rules in field_rules.items():
            value = data.get(field_name)

            # Check required
            if rules.get("required", False) and not value:
                raise HTTPException(
                    status_code=400,
                    detail=f"{field_name} is required"
                )

            if value is None:
                continue

            # Sanitize based on type
            field_type = rules.get("type", "string")

            if field_type == "email":
                sanitized[field_name] = InputSanitizer.sanitize_email(value)
            elif field_type == "phone":
                sanitized[field_name] = InputSanitizer.sanitize_phone(value)
            elif field_type == "string":
                sanitized[field_name] = InputSanitizer.sanitize_string(
                    value,
                    max_length=rules.get("max_length"),
                    allow_html=rules.get("allow_html", False),
                    field_name=field_name
                )
            else:
                sanitized[field_name] = value

        return sanitized


# Example usage in endpoints
def sanitize_support_request(data: dict) -> dict:
    """Sanitize support request data"""
    rules = {
        "name": {
            "type": "string",
            "required": True,
            "max_length": 100,
            "allow_html": False
        },
        "email": {
            "type": "email",
            "required": True
        },
        "phone": {
            "type": "phone",
            "required": False
        },
        "subject": {
            "type": "string",
            "required": True,
            "max_length": 200,
            "allow_html": False
        },
        "message": {
            "type": "string",
            "required": True,
            "max_length": 5000,
            "allow_html": False
        },
        "priority": {
            "type": "string",
            "required": False,
            "max_length": 20
        },
        "category": {
            "type": "string",
            "required": False,
            "max_length": 50
        }
    }

    return InputSanitizer.sanitize_dict(data, rules)
