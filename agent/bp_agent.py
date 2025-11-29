"""Blood Pressure Agent for generating guidance via OpenAI."""

import os
from typing import Optional

import openai


class BPAgent:
    """Simple wrapper around OpenAI chat completions for BP guidance."""

    def __init__(
        self,
        *,
        api_key: Optional[str] = None,
        model: str = "gpt-5-chat-latest",
    ) -> None:
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY env var (or api_key) is required")
        self.client = openai.OpenAI(api_key=self.api_key)
        self.model = model

    def generate_guidance(
        self, systolic: int, diastolic: int, heart_rate: int, symptoms: str
    ) -> str:
        """Produce AI guidance for a single blood pressure reading."""
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a helpful assistant that generates guidance for "
                        "blood pressure readings. Don't end with a question."
                        "Provide as much comprehensive guidance as possible."
                    ),
                },
                {
                    "role": "user",
                    "content": (
                        "Systolic: {systolic}, Diastolic: {diastolic}, "
                        "Heart Rate: {heart_rate}, Symptoms: {symptoms}"
                    ).format(
                        systolic=systolic,
                        diastolic=diastolic,
                        heart_rate=heart_rate,
                        symptoms=symptoms,
                    ),
                },
            ],
        )
        return response.choices[0].message.content
