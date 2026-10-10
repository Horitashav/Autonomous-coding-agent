"""Output Guard — PII Redaction & Output Validation."""

import re
from dataclasses import dataclass, field

PII_PATTERNS: list[tuple[re.Pattern, str, str]] = [
    (re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'), "[EMAIL_REDACTED]", "email"),
    (re.compile(r'(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b'), "[PHONE_REDACTED]", "phone"),
    (re.compile(r'\b\d{3}[-\s]?\d{2}[-\s]?\d{4}\b'), "[SSN_REDACTED]", "ssn"),
    (re.compile(r'\b(?:sk-(?:proj-|ant-)?[A-Za-z0-9]{20,}|ghp_[A-Za-z0-9]{36,}|xox[bpars]-[A-Za-z0-9-]{10,})\b'), "[API_KEY_REDACTED]", "api_key"),
    (re.compile(r'\b(?:\d{4}[-\s]?){3}\d{4}\b'), "[CC_REDACTED]", "credit_card"),
    (re.compile(r'\b(?:(?:25[0-5]|2[0-4]\d|[01]?\d\d?)\.){3}(?:25[0-5]|2[0-4]\d|[01]?\d\d?)\b'), "[IP_REDACTED]", "ip_address"),
]


@dataclass
class RedactionResult:
    redacted_text: str
    redaction_count: int = 0
    redacted_types: list[str] = field(default_factory=list)

    @property
    def had_pii(self) -> bool:
        return self.redaction_count > 0


def redact_pii(text: str) -> RedactionResult:
    redacted = text
    total_count = 0
    found_types: list[str] = []

    for pattern, replacement, pii_type in PII_PATTERNS:
        matches = pattern.findall(redacted)
        if matches:
            count = len(matches)
            redacted = pattern.sub(replacement, redacted)
            total_count += count
            if pii_type not in found_types:
                found_types.append(pii_type)

    return RedactionResult(
        redacted_text=redacted,
        redaction_count=total_count,
        redacted_types=found_types,
    )