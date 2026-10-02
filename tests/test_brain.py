"""Tests for Brain module with mocked LLM responses."""

from unittest.mock import MagicMock

from agent.brain.code_generator import CodeGenerator, extract_code
from agent.brain.llm_client import LLMResponse
from agent.brain.planner import Planner


class TestExtractCode:
    """Verify code extraction from markdown responses."""

    def test_extracts_from_python_fence(self):
        raw = '```python\nprint("hello")\n```'
        assert extract_code(raw) == 'print("hello")'

    def test_extracts_from_generic_fence(self):
        raw = '```\nprint("hello")\n```'
        assert extract_code(raw) == 'print("hello")'

    def test_handles_raw_code_no_fences(self):
        raw = 'print("hello")'
        assert extract_code(raw) == 'print("hello")'


class TestCodeGenerator:
    """Verify code generation and repair workflows using mocks."""

    def _make_mock_client(self, content: str) -> MagicMock:
        mock_client = MagicMock()
        mock_client.generate.return_value = LLMResponse(
            content=content,
            model="gpt-4o-mini",
            input_tokens=100,
            output_tokens=50,
            finish_reason="stop",
        )
        return mock_client

    def test_generate_simple_code(self):
        mock = self._make_mock_client('print("test")')
        generator = CodeGenerator(llm_client=mock)
        result = generator.generate("Print test")

        assert result.code == 'print("test")'
        assert not result.was_truncated
        mock.generate.assert_called_once()

    def test_repair_includes_error(self):
        mock = self._make_mock_client('print("fixed")')
        generator = CodeGenerator(llm_client=mock)
        result = generator.repair(
            task_description="Divide",
            failed_code="1/0",
            error_output="ZeroDivisionError",
            attempt_number=1,
            max_attempts=3,
        )

        assert result.code == 'print("fixed")'
        mock.generate.assert_called_once()


class TestPlanner:
    """Verify pre-execution analysis logic."""

    def test_planner_identifies_infeasible_network_task(self):
        json_content = """
        {
            "task_summary": "Scrape website",
            "approach": "requests.get",
            "required_libraries": ["requests"],
            "estimated_complexity": "moderate",
            "potential_issues": ["No internet"],
            "requires_network": true,
            "requires_file_io": false,
            "is_destructive": false
        }
        """
        mock = MagicMock()
        mock.generate.return_value = LLMResponse(
            content=json_content,
            model="gpt-4o-mini",
            input_tokens=50,
            output_tokens=50,
            finish_reason="stop",
        )

        planner = Planner(llm_client=mock)
        plan = planner.analyze("Scrape example.com")

        assert not plan.is_feasible
        assert plan.requires_network
