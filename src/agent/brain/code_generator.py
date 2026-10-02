import logging
import re
from dataclasses import dataclass

from agent.brain.llm_client import LLMClient, LLMResponse
from agent.brain.prompts import (
    CODE_GENERATION_USER_TEMPLATE,
    CODE_GENERATOR_SYSTEM_PROMPT,
    REPAIR_SYSTEM_PROMPT,
    REPAIR_USER_TEMPLATE,
)
from agent.config import MAX_CODE_LENGTH

logger = logging.getLogger(__name__)


@dataclass
class CodeGenerationResult:
    """Result of a code generation attempt."""

    code: str
    llm_response: LLMResponse
    was_truncated: bool = False


def extract_code(raw_response: str) -> str:
    """Strip markdown code fences and whitespace from LLM output."""
    # Pattern 1: ```python ... ```
    pattern_python = r"```python\s*\n(.*?)```"
    match = re.search(pattern_python, raw_response, re.DOTALL)
    if match:
        return match.group(1).strip()

    # Pattern 2: ``` ... ``` (generic fence)
    pattern_generic = r"```\s*\n(.*?)```"
    match = re.search(pattern_generic, raw_response, re.DOTALL)
    if match:
        return match.group(1).strip()

    # Pattern 3: Clean text
    return raw_response.strip()


class CodeGenerator:
    """Generates and repairs Python code via LLM."""

    def __init__(self, llm_client: LLMClient | None = None):
        self.llm_client = llm_client or LLMClient()

    def generate(self, task_description: str) -> CodeGenerationResult:
        """Generate code from a natural language prompt."""
        user_prompt = CODE_GENERATION_USER_TEMPLATE.format(task_description=task_description)

        response = self.llm_client.generate(
            system_prompt=CODE_GENERATOR_SYSTEM_PROMPT,
            user_prompt=user_prompt,
        )

        code = extract_code(response.content)

        if len(code) > MAX_CODE_LENGTH:
            raise ValueError(f"Generated code is {len(code)} characters (max: {MAX_CODE_LENGTH}).")

        return CodeGenerationResult(
            code=code,
            llm_response=response,
            was_truncated=(response.finish_reason == "length"),
        )

    def repair(
        self,
        task_description: str,
        failed_code: str,
        error_output: str,
        attempt_number: int,
        max_attempts: int,
    ) -> CodeGenerationResult:
        """Repair failed code using traceback and error context."""
        user_prompt = REPAIR_USER_TEMPLATE.format(
            task_description=task_description,
            failed_code=failed_code,
            error_output=error_output,
            attempt_number=attempt_number,
            max_attempts=max_attempts,
        )

        response = self.llm_client.generate(
            system_prompt=REPAIR_SYSTEM_PROMPT,
            user_prompt=user_prompt,
        )

        code = extract_code(response.content)

        if len(code) > MAX_CODE_LENGTH:
            raise ValueError(f"Repaired code exceeds max length ({len(code)} chars).")

        return CodeGenerationResult(
            code=code,
            llm_response=response,
            was_truncated=(response.finish_reason == "length"),
        )
