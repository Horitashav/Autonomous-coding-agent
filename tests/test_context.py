"""Tests for the multi-file context system."""

import pytest
from agent.context.context_builder import ContextBuilder
from agent.context.file_ingester import FileIngester
from agent.context.token_counter import TokenCounter


@pytest.fixture
def sample_project(tmp_path):
    """Create a temporary project structure with varied file types."""
    (tmp_path / "main.py").write_text('print("hello")\n')
    (tmp_path / "utils.py").write_text("def add(a, b):\n    return a + b\n")
    (tmp_path / "README.md").write_text("# Test Project\nA sample project.\n")
    (tmp_path / "config.json").write_text('{"debug": true}\n')

    src = tmp_path / "src"
    src.mkdir()
    (src / "app.py").write_text("from utils import add\nprint(add(1, 2))\n")
    (src / "database.py").write_text("class Database:\n    pass\n")

    # Folders that MUST be pruned
    cache = tmp_path / "__pycache__"
    cache.mkdir()
    (cache / "main.pyc").write_bytes(b"junk")

    git = tmp_path / ".git"
    git.mkdir()
    (git / "HEAD").write_text("ref: refs/heads/main\n")

    # File that exceeds size limit
    (tmp_path / "huge_data.py").write_text("x = 1\n" * 50000)

    return tmp_path


class TestTokenCounter:
    def test_count_simple_text(self):
        counter = TokenCounter()
        assert counter.count("Hello, world!") > 0

    def test_count_empty_string(self):
        assert TokenCounter().count("") == 0

    def test_truncate_respects_budget(self):
        counter = TokenCounter()
        truncated = counter.truncate_to_budget("word " * 1000, max_tokens=50)
        assert counter.count(truncated) <= 65

    def test_fits_budget_check(self):
        counter = TokenCounter()
        assert counter.fits_budget("short text", max_tokens=100)
        assert not counter.fits_budget("word " * 1000, max_tokens=10)


class TestFileIngester:
    def test_discover_finds_python_files(self, sample_project):
        ingester = FileIngester(str(sample_project))
        paths = [f.relative_path for f in ingester.discover()]
        assert "main.py" in paths
        assert "utils.py" in paths
        assert "src/app.py" in paths

    def test_discover_skips_pycache_and_git(self, sample_project):
        ingester = FileIngester(str(sample_project))
        paths = [f.relative_path for f in ingester.discover()]
        assert not any("__pycache__" in p for p in paths)
        assert not any(".git" in p for p in paths)

    def test_discover_skips_large_files(self, sample_project):
        ingester = FileIngester(str(sample_project))
        paths = [f.relative_path for f in ingester.discover()]
        assert "huge_data.py" not in paths

    def test_get_tree_string(self, sample_project):
        ingester = FileIngester(str(sample_project))
        tree = ingester.get_tree_string()
        assert "main.py" in tree
        assert "src/" in tree or "src" in tree


class TestContextBuilder:
    def test_relevance_scoring_prioritizes_query_match(self, sample_project):
        builder = ContextBuilder(str(sample_project))
        result = builder.build("Fix the database connection", token_budget=10_000)
        assert "src/database.py" in result.included_files

    def test_respects_token_budget(self, sample_project):
        builder = ContextBuilder(str(sample_project))
        result = builder.build("Some task", token_budget=500)
        assert result.total_tokens <= 500
        assert result.utilization <= 100.0

    def test_empty_directory_handling(self, tmp_path):
        builder = ContextBuilder(str(tmp_path))
        result = builder.build("Some task", token_budget=10_000)
        assert "No project files found" in result.context_text