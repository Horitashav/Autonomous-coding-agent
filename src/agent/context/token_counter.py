"""
Token Counter — Accurate token counting and budget truncation using tiktoken.
"""

import tiktoken


class TokenCounter:
    """Counts tokens accurately using tiktoken encodings."""

    def __init__(self, model: str = "openai/gpt-oss-120b"):
        """Initialize with tokenizer encoding."""
        try:
            self.encoding = tiktoken.encoding_for_model(model)
        except KeyError:
            # Fallback to cl100k_base if model name is unrecognized
            self.encoding = tiktoken.get_encoding("cl100k_base")

    def count(self, text: str) -> int:
        """Count the exact number of tokens in a text string."""
        return len(self.encoding.encode(text))

    def count_file(self, filepath: str, content: str) -> int:
        """Count tokens for a file including its markdown syntax fence header."""
        header = f"### File: {filepath}\n```\n"
        footer = "\n```\n"
        full_text = header + content + footer
        return self.count(full_text)

    def truncate_to_budget(self, text: str, max_tokens: int) -> str:
        """Truncate text to fit within a token budget."""
        tokens = self.encoding.encode(text)
        if len(tokens) <= max_tokens:
            return text

        truncated_tokens = tokens[:max_tokens]
        truncated_text = self.encoding.decode(truncated_tokens)
        return truncated_text + "\n... [TRUNCATED — exceeded token budget]"

    def fits_budget(self, text: str, max_tokens: int) -> bool:
        """Check if text fits within a token budget."""
        return self.count(text) <= max_tokens
