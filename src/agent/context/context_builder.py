"""
Context Builder — Assembles ranked project files into structured prompt context.
"""

import logging
import re
from dataclasses import dataclass, field

from agent.context.file_ingester import FileIngester, ProjectFile
from agent.context.token_counter import TokenCounter

logger = logging.getLogger(__name__)


@dataclass
class ContextResult:
    """The formatted context ready for LLM prompt injection."""

    context_text: str
    included_files: list[str] = field(default_factory=list)
    excluded_files: list[str] = field(default_factory=list)
    total_tokens: int = 0
    token_budget: int = 0

    @property
    def utilization(self) -> float:
        """Percentage of the token budget consumed."""
        if self.token_budget == 0:
            return 0.0
        return round(self.total_tokens / self.token_budget * 100, 1)


class ContextBuilder:
    """Scores, filters, and formats project context within a token budget."""

    def __init__(self, project_root: str):
        self.ingester = FileIngester(project_root)
        self.counter = TokenCounter()

    def build(
        self,
        user_prompt: str,
        token_budget: int = 20_000,
    ) -> ContextResult:
        """Assemble structured context based on prompt relevance and budget."""
        all_files = self.ingester.discover()

        if not all_files:
            return ContextResult(
                context_text="(No project files found)",
                token_budget=token_budget,
            )

        scored = self._score_files(all_files, user_prompt)
        tree = self.ingester.get_tree_string()
        tree_section = f"### Project Structure\n```\n{tree}\n```\n\n"
        tree_tokens = self.counter.count(tree_section)

        remaining_budget = token_budget - tree_tokens
        included: list[ProjectFile] = []
        excluded: list[str] = []
        total_tokens = tree_tokens

        # Greedily include files ordered by relevance score
        for pf, _score in scored:
            self.ingester.load_files([pf])
            file_tokens = self.counter.count_file(pf.relative_path, pf.content)
            pf.token_count = file_tokens

            if file_tokens <= remaining_budget:
                included.append(pf)
                remaining_budget -= file_tokens
                total_tokens += file_tokens
            else:
                excluded.append(pf.relative_path)

        # Assemble the markdown context section
        context_parts = ["## Project Context\n\n", tree_section]
        for pf in included:
            lang = pf.language if pf.language != "unknown" else ""
            context_parts.append(
                f"### File: {pf.relative_path}\n"
                f"```{lang}\n{pf.content}\n```\n\n"
            )

        context_text = "".join(context_parts)
        return ContextResult(
            context_text=context_text,
            included_files=[f.relative_path for f in included],
            excluded_files=excluded,
            total_tokens=total_tokens,
            token_budget=token_budget,
        )

    def _score_files(
        self,
        files: list[ProjectFile],
        user_prompt: str,
    ) -> list[tuple[ProjectFile, float]]:
        """Score files based on keyword overlap and semantic hints."""
        prompt_lower = user_prompt.lower()
        prompt_words = set(re.findall(r"\w+", prompt_lower))

        scored: list[tuple[ProjectFile, float]] = []

        for pf in files:
            score = 0.0
            path_lower = pf.relative_path.lower()
            path_words = set(re.findall(r"\w+", path_lower))

            # Direct word overlap in file path
            overlap = prompt_words & path_words
            score += len(overlap) * 10

            # Language hints in prompt
            lang_hints = {
                "python": [".py"],
                "javascript": [".js", ".jsx"],
                "typescript": [".ts", ".tsx"],
                "css": [".css"],
                "html": [".html"],
                "sql": [".sql"],
            }
            for hint, exts in lang_hints.items():
                if hint in prompt_lower and pf.extension in exts:
                    score += 5

            # Structural files boost
            if "readme" in path_lower or path_lower.endswith(".md"):
                score += 3

            if "config" in path_lower or "settings" in path_lower:
                score += 2

            # Small focused files preference
            if pf.size_bytes < 5000:
                score += 1

            scored.append((pf, score))

        scored.sort(key=lambda x: (-x[1], x[0].relative_path))
        return scored