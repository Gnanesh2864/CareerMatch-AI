import re
from typing import List, Optional

PROMPT_INJECTION_PATTERNS = [
    r'ignore\s+previous\s+instructions',
    r'disregard\s+all\s+prior',
    r'system\s+prompt',
    r'you\s+are\s+now\s+in\s+developer\s+mode',
    r'reveal\s+(?:your|the)\s+secret',
    r'drop\s+table',
    r'<script',
    r'bash\s+-c',
]

def sanitize_untrusted_text(text: str) -> str:
    """
    Sanitizes untrusted text (such as user resumes and job descriptions)
    to neutralize prompt injection and control character exploits.
    """
    if not text:
        return ""

    sanitized = text
    for pattern in PROMPT_INJECTION_PATTERNS:
        sanitized = re.sub(pattern, '[REDACTED_SUSPICIOUS_INPUT]', sanitized, flags=re.IGNORECASE)

    # Neutralize control characters
    sanitized = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', sanitized)
    return sanitized.strip()

def wrap_untrusted_context(tag_name: str, content: str) -> str:
    """Wraps untrusted content into isolated XML boundaries with explicit system instructions."""
    clean_content = sanitize_untrusted_text(content)
    return f"<{tag_name}>\n{clean_content}\n</{tag_name}>"
