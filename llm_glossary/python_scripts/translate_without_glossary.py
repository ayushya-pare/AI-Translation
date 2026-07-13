import os
import sys

import requests


API_KEY = os.getenv("API_KEY")
BASE_URL = os.getenv("BASE_URL", "https://openwebui-test.hrz.uni-bonn.de/api")
MODEL = os.getenv("MODEL_NAME", "local.openai/gpt-oss-120b")
REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", "60"))


if not API_KEY:
    raise SystemExit("Set API_KEY first.")


def input_text():
    if len(sys.argv) > 1:
        return " ".join(sys.argv[1:]).strip()
    return sys.stdin.read().strip()


german_text = input_text()
if not german_text:
    raise SystemExit("Pass German text as an argument or via stdin.")


try:
    response = requests.post(
        f"{BASE_URL}/chat/completions",
        headers={
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json",
        },
        json={
            "model": MODEL,
            "messages": [
                {
                    "role": "user",
                    "content": f"""Translate this German text into English.
Return only the English translation. Do not use Markdown or explanations.

German:
{german_text}

English:""",
                }
            ],
            "temperature": 0,
        },
        timeout=REQUEST_TIMEOUT,
    )
    response.raise_for_status()
except requests.RequestException as error:
    raise SystemExit(
        "Translation without glossary failed while calling "
        f"{BASE_URL}/chat/completions: {error}"
    ) from error

translation = response.json()["choices"][0]["message"]["content"].strip()

print(translation)
