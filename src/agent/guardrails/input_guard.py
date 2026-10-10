"""Input Guard — Detects prompt injection and adversarial attacks."""

import re
from dataclasses import dataclass, field


@dataclass
class GuardResult:
    """Result of an input safety check."""

    is_safe: bool
    risk_level: str = "low"  # "low", "medium", "high"
    triggered_rules: list[str] = field(default_factory=list)
    sanitized_input: str | None = None


# Patterns derived from security research targeting LLMs
INJECTION_PATTERNS: list[tuple[re.Pattern, str, str]] = [
    # Direct instruction overrides (covers "ignore instructions", "ignore all instructions", "ignore prior instructions")
    (
        re.compile(r"ignore\s+(all\s+)?(previous\s+|prior\s+)?instructions?", re.IGNORECASE),
        "instruction_override",
        "high",
    ),
    (
        re.compile(
            r"disregard\s+(all\s+)?(previous\s+|prior\s+|above\s+)?(instructions?|rules|guidelines)?",
            re.IGNORECASE,
        ),
        "instruction_disregard",
        "high",
    ),
    (
        re.compile(
            r"forget\s+(all\s+)?(previous\s+|prior\s+|your\s+)?(instructions?|rules)",
            re.IGNORECASE,
        ),
        "instruction_forget",
        "high",
    ),
    # System environment and secret exfiltration
    (
        re.compile(r"os\.environ", re.IGNORECASE),
        "env_access_attempt",
        "high",
    ),
    (
        re.compile(
            r"(show|reveal|display|print|leak)\s+(all\s+)?(the\s+)?(secret|env|environment|api[_\s]key)",
            re.IGNORECASE,
        ),
        "env_leak_attempt",
        "high",
    ),
    # Persona / Role hijacking
    (
        re.compile(r"you\s+are\s+now\s+(a|an)\s+", re.IGNORECASE),
        "role_hijack",
        "high",
    ),
    (
        re.compile(r"act\s+as\s+(a|an)\s+(unrestricted|unfiltered|uncensored)", re.IGNORECASE),
        "role_hijack_unrestricted",
        "high",
    ),
    (
        re.compile(r"pretend\s+(you\s+are|to\s+be)\s+", re.IGNORECASE),
        "role_pretend",
        "medium",
    ),
    (
        re.compile(r"new\s+system\s+prompt", re.IGNORECASE),
        "system_prompt_override",
        "high",
    ),
    # System prompt extraction
    (
        re.compile(
            r"(show|reveal|display|print|output)\s+(your|the)\s+system\s+prompt",
            re.IGNORECASE,
        ),
        "prompt_extraction",
        "high",
    ),
    (
        re.compile(
            r"what\s+(are|is)\s+your\s+(instructions|system\s+prompt|rules)",
            re.IGNORECASE,
        ),
        "prompt_extraction_question",
        "medium",
    ),
    # Encoded payloads
    (
        re.compile(r"base64[:\s]", re.IGNORECASE),
        "encoded_payload_hint",
        "medium",
    ),
    (
        re.compile(r"\\x[0-9a-fA-F]{2}", re.IGNORECASE),
        "hex_escape_sequence",
        "medium",
    ),
    # Destructive host commands
    (
        re.compile(r"(rm\s+-rf|format\s+[cC]:|del\s+/[fFsS])", re.IGNORECASE),
        "destructive_command",
        "high",
    ),
    (
        re.compile(r"(curl|wget|nc|netcat)\s+", re.IGNORECASE),
        "network_command",
        "medium",
    ),
    # Delimiter / Template injections
    (
        re.compile(r"<\|?(system|assistant|user)\|?>", re.IGNORECASE),
        "delimiter_injection",
        "high",
    ),
    (
        re.compile(r"\[INST\]|\[/INST\]|<<SYS>>|<</SYS>>", re.IGNORECASE),
        "llama_delimiter_injection",
        "high",
    ),
]


def check_input_safety(user_input: str) -> GuardResult:
    """Check user input for prompt injection and adversarial patterns."""
    triggered: list[str] = []
    max_risk = "low"

    # Layer 1: Length check (unusually massive prompts often conceal injection payloads)
    if len(user_input) > 5000:
        triggered.append("excessive_length")
        max_risk = "medium"

    if not user_input.strip():
        return GuardResult(
            is_safe=True,
            risk_level="low",
            triggered_rules=[],
            sanitized_input=user_input,
        )

    # Layer 2: Known injection pattern matching
    for pattern, rule_name, risk_level in INJECTION_PATTERNS:
        if pattern.search(user_input):
            triggered.append(rule_name)
            if risk_level == "high":
                max_risk = "high"
            elif risk_level == "medium" and max_risk != "high":
                max_risk = "medium"

    # Layer 3: Structural heuristics (excessive special characters)
    special_char_ratio = sum(1 for c in user_input if not c.isalnum() and not c.isspace()) / max(
        len(user_input), 1
    )

    if special_char_ratio > 0.4:
        triggered.append("high_special_char_ratio")
        if max_risk == "low":
            max_risk = "medium"

    # Block if high risk
    is_safe = max_risk != "high"

    return GuardResult(
        is_safe=is_safe,
        risk_level=max_risk,
        triggered_rules=triggered,
        sanitized_input=user_input.strip(),
    )
