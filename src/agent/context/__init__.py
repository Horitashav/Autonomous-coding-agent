"""
Context module — Multi-file project ingestion for LLM context building.
"""

from agent.context.context_builder import ContextBuilder, ContextResult
from agent.context.file_ingester import FileIngester, ProjectFile
from agent.context.token_counter import TokenCounter

__all__ = [
    "FileIngester",
    "ProjectFile",
    "ContextBuilder",
    "ContextResult",
    "TokenCounter",
]