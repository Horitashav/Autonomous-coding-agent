"""
File Ingester — Discovers and reads project source files for LLM context.
"""

import logging
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Generator

logger = logging.getLogger(__name__)


@dataclass
class ProjectFile:
    """Represents a discovered file and its metadata."""

    relative_path: str
    absolute_path: str
    content: str = ""
    size_bytes: int = 0
    extension: str = ""
    language: str = "unknown"
    token_count: int = 0

    @property
    def is_loaded(self) -> bool:
        """Return True if content has been read from disk."""
        return len(self.content) > 0


# File extensions we recognize as useful source code
SUPPORTED_EXTENSIONS: dict[str, str] = {
    ".py": "python",
    ".js": "javascript",
    ".jsx": "javascript",
    ".ts": "typescript",
    ".tsx": "typescript",
    ".html": "html",
    ".css": "css",
    ".json": "json",
    ".yaml": "yaml",
    ".yml": "yaml",
    ".toml": "toml",
    ".ini": "ini",
    ".cfg": "config",
    ".md": "markdown",
    ".txt": "text",
    ".sql": "sql",
    ".sh": "shell",
    ".bash": "shell",
    ".dockerfile": "dockerfile",
}

# Directories to skip entirely
SKIP_DIRECTORIES: set[str] = {
    ".git",
    ".svn",
    ".hg",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    "node_modules",
    "bower_components",
    ".venv",
    "venv",
    "env",
    "dist",
    "build",
    ".idea",
    ".vscode",
    ".run_history",
}

# Maximum file size to load (100KB cutoff)
MAX_FILE_SIZE_BYTES: int = 100_000


class FileIngester:
    """Discovers and selectively loads project files."""

    def __init__(
        self,
        project_root: str,
        max_file_size: int = MAX_FILE_SIZE_BYTES,
        extra_skip_dirs: set[str] | None = None,
    ):
        self.project_root = Path(project_root).resolve()
        self.max_file_size = max_file_size
        self.skip_dirs = SKIP_DIRECTORIES | (extra_skip_dirs or set())

        if not self.project_root.is_dir():
            raise ValueError(f"Project root is not a directory: {self.project_root}")

    def discover(self) -> list[ProjectFile]:
        """Walk the directory tree and collect metadata without loading contents."""
        files: list[ProjectFile] = []

        for file_path in self._walk_directory():
            ext = file_path.suffix.lower()

            if ext not in SUPPORTED_EXTENSIONS:
                if file_path.name.lower().startswith("dockerfile"):
                    ext = ".dockerfile"
                else:
                    continue

            try:
                size = file_path.stat().st_size
            except OSError:
                continue

            # Skip empty files or oversized files
            if size > self.max_file_size or size == 0:
                continue

            relative = str(file_path.relative_to(self.project_root)).replace("\\", "/")

            files.append(
                ProjectFile(
                    relative_path=relative,
                    absolute_path=str(file_path),
                    size_bytes=size,
                    extension=ext,
                    language=SUPPORTED_EXTENSIONS.get(ext, "unknown"),
                )
            )

        files.sort(key=lambda f: f.relative_path)
        logger.info(f"Discovered {len(files)} files in {self.project_root}")
        return files

    def load_files(self, files: list[ProjectFile]) -> list[ProjectFile]:
        """Load file contents lazily from disk into memory."""
        loaded_count = 0
        for pf in files:
            if pf.is_loaded:
                continue

            try:
                with open(pf.absolute_path, "r", encoding="utf-8", errors="replace") as f:
                    pf.content = f.read()
                loaded_count += 1
            except Exception as e:
                logger.warning(f"Failed to read {pf.relative_path}: {e}")
                pf.content = f"[Error reading file: {e}]"

        logger.info(f"Loaded {loaded_count} files from disk")
        return files

    def _walk_directory(self) -> Generator[Path, None, None]:
        """Recursively walk directory while pruning ignored subtrees in-place."""
        for dirpath, dirnames, filenames in os.walk(self.project_root):
            # Prune directories in-place so os.walk does not descend into them
            dirnames[:] = [
                d
                for d in dirnames
                if d not in self.skip_dirs and not d.startswith(".")
            ]
            for filename in filenames:
                yield Path(dirpath) / filename

    def get_tree_string(self) -> str:
        """Generate a formatted visual tree representation of the project."""
        lines: list[str] = []
        for dirpath, dirnames, filenames in os.walk(self.project_root):
            dirnames[:] = [
                d
                for d in dirnames
                if d not in self.skip_dirs and not d.startswith(".")
            ]
            dirnames.sort()

            rel_dir = Path(dirpath).relative_to(self.project_root)
            depth = len(rel_dir.parts)
            indent = "  " * depth

            if depth > 0:
                lines.append(f"{indent}{rel_dir.name}/")

            for fn in sorted(filenames):
                ext = Path(fn).suffix.lower()
                if ext in SUPPORTED_EXTENSIONS or fn.lower().startswith("dockerfile"):
                    lines.append(f"{indent}  {fn}")

        return "\n".join(lines)