from __future__ import annotations

import logging
import time

log = logging.getLogger(__name__)


class GeminiAnalyst:
    """Thin wrapper around the Gemini API (google-genai SDK) with retry/backoff."""

    def __init__(
        self,
        api_key: str,
        model: str = "gemini-2.5-flash",
        temperature: float = 0.4,
        max_retries: int = 3,
    ) -> None:
        from google import genai  # lazy: dry-runs and tests don't need the SDK

        self._types = __import__("google.genai.types", fromlist=["types"])
        self.client = genai.Client(api_key=api_key)
        self.model = model
        self.temperature = temperature
        self.max_retries = max_retries

    def generate(self, system_prompt: str, user_prompt: str) -> str:
        config = self._types.GenerateContentConfig(
            system_instruction=system_prompt,
            temperature=self.temperature,
            max_output_tokens=8192,  # thinking tokens count toward this on 2.5 models
        )
        for attempt in range(1, self.max_retries + 1):
            try:
                response = self.client.models.generate_content(
                    model=self.model, contents=user_prompt, config=config
                )
                if not response.text:
                    raise RuntimeError("Gemini returned an empty response")
                return response.text.strip()
            except Exception as exc:
                log.warning("Gemini call failed (attempt %d/%d): %s", attempt, self.max_retries, exc)
                if attempt == self.max_retries:
                    raise
                time.sleep(2**attempt)
        raise RuntimeError("unreachable")
