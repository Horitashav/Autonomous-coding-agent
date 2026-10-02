"""LLM Client — Adapter wrapper around LLM providers."""

import logging
from dataclasses import dataclass

from openai import OpenAI

from agent.config import LLM_MODEL, LLM_TEMPERATURE, OPENAI_API_KEY

logger = logging.getLogger(__name__)


@dataclass
class LLMResponse:
    """Standardized response container from any LLM provider."""

    content: str  # Generated text
    model: str  # Model used
    input_tokens: int  # Prompt tokens consumed
    output_tokens: int  # Completion tokens generated
    finish_reason: str  # 'stop' (finished cleanly) or 'length' (hit cutoff)

    @property
    def total_tokens(self) -> int:
        """Total tokens used in this call."""
        return self.input_tokens + self.output_tokens

    @property
    def estimated_cost_usd(self) -> float:
        """Estimated cost using gpt-4o-mini baseline pricing."""
        input_cost = (self.input_tokens / 1_000_000) * 0.15
        output_cost = (self.output_tokens / 1_000_000) * 0.60
        return round(input_cost + output_cost, 6)


class LLMClient:
    """Wrapper around chat completion APIs."""

    def __init__(
        self,
        model: str = LLM_MODEL,
        temperature: float = LLM_TEMPERATURE,
        api_key: str = OPENAI_API_KEY,
    ):
        if not api_key:
            raise ValueError("No OpenAI API key found. Set OPENAI_API_KEY in your .env file.")

        self.model = model
        self.temperature = temperature
        self.client = OpenAI(api_key=api_key)

    def generate(
        self,
        system_prompt: str,
        user_prompt: str,
        max_tokens: int = 4096,
    ) -> LLMResponse:
        """Single-turn generation from system and user prompt."""
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=self.temperature,
                max_tokens=max_tokens,
            )

            choice = response.choices[0]
            usage = response.usage

            return LLMResponse(
                content=choice.message.content or "",
                model=response.model,
                input_tokens=usage.prompt_tokens if usage else 0,
                output_tokens=usage.completion_tokens if usage else 0,
                finish_reason=choice.finish_reason or "unknown",
            )
        except Exception as e:
            logger.error(f"LLM API call failed: {e}")
            raise RuntimeError(f"Failed to get LLM response: {e}") from e

    def generate_with_history(
        self,
        system_prompt: str,
        messages: list[dict[str, str]],
        max_tokens: int = 4096,
    ) -> LLMResponse:
        """Multi-turn generation with full conversation history."""
        full_messages = [{"role": "system", "content": system_prompt}]
        full_messages.extend(messages)

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=full_messages,
                temperature=self.temperature,
                max_tokens=max_tokens,
            )

            choice = response.choices[0]
            usage = response.usage

            return LLMResponse(
                content=choice.message.content or "",
                model=response.model,
                input_tokens=usage.prompt_tokens if usage else 0,
                output_tokens=usage.completion_tokens if usage else 0,
                finish_reason=choice.finish_reason or "unknown",
            )
        except Exception as e:
            logger.error(f"LLM API call with history failed: {e}")
            raise RuntimeError(f"Failed to get LLM response: {e}") from e
