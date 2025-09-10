import os
from typing import Optional

try:
    from openai import AzureOpenAI
except Exception:
    # Fallback for environments without the new package naming
    from openai import OpenAI as AzureOpenAI  # type: ignore


class OpenAIClient:
    """Light wrapper for Azure OpenAI chat completions.

    Expects the following environment variables to be set:
      - AZURE_OPENAI_ENDPOINT
      - AZURE_OPENAI_KEY
      - AZURE_OPENAI_DEPLOYMENT (model deployment name, e.g. gpt-4.1-mini)
      - AZURE_OPENAI_API_VERSION (optional, default '2024-12-01-preview')
    """

    def __init__(self):
        self.endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
        self.api_key = os.getenv("AZURE_OPENAI_KEY")
        self.deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT")
        self.api_version = os.getenv("AZURE_OPENAI_API_VERSION", "2024-12-01-preview")

        if not self.endpoint or not self.api_key or not self.deployment:
            raise ValueError(
                "AZURE_OPENAI_ENDPOINT, AZURE_OPENAI_KEY and AZURE_OPENAI_DEPLOYMENT must be set"
            )

        # Initialize client
        self.client = AzureOpenAI(
            api_version=self.api_version,
            azure_endpoint=self.endpoint,
            api_key=self.api_key,
        )

    def chat_completion(
        self,
        user_message: str,
        system_instruction: Optional[str] = "You are a helpful assistant.",
        temperature: float = 1.0,
        top_p: float = 1.0,
        max_tokens: int = 512,
    ) -> str:
        messages = [
            {"role": "system", "content": system_instruction},
            {"role": "user", "content": user_message},
        ]

        resp = self.client.chat.completions.create(
            messages=messages,
            max_completion_tokens=max_tokens,
            temperature=temperature,
            top_p=top_p,
            model=self.deployment,
        )

        # Safety: navigate response structure defensively
        try:
            return resp.choices[0].message.content
        except Exception:
            # If structure differs, try alternative access
            try:
                return resp.choices[0].text
            except Exception:
                return ""
