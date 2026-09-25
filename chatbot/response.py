import json
import os
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


class AIResponseGenerator:
    """Generate answers through an OpenAI-compatible chat completions API."""

    def __init__(self):
        self.api_key = os.environ.get("OPENAI_API_KEY", "").strip()
        self.endpoint = os.environ.get(
            "OPENAI_API_URL", "https://api.openai.com/v1/chat/completions"
        )
        self.model = os.environ.get("OPENAI_MODEL", "gpt-4o-mini")

    @property
    def enabled(self):
        return bool(self.api_key)

    def answer(self, question):
        if not self.enabled:
            return None

        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "You are Emerspark Assistant. Answer the user's question clearly, "
                        "accurately, and concisely. If the question needs current or "
                        "private information you do not have, say so instead of inventing it."
                    ),
                },
                {"role": "user", "content": question},
            ],
            "temperature": 0.4,
        }
        request = Request(
            self.endpoint,
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            method="POST",
        )
        try:
            with urlopen(request, timeout=30) as response:
                result = json.loads(response.read().decode("utf-8"))
            return result["choices"][0]["message"]["content"].strip()
        except (HTTPError, URLError, TimeoutError, KeyError, IndexError, json.JSONDecodeError):
            return None
