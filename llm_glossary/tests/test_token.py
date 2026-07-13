import os

import requests


API_KEY = os.getenv("API_KEY")
BASE_URL = os.getenv("BASE_URL", "https://openwebui-test.hrz.uni-bonn.de/api")
MODEL = os.getenv("MODEL_NAME", "local.openai/gpt-oss-120b")

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json",
}
payload = {
    "model": MODEL,
    "messages": [
        {
            "role": "user",
            "content": "Translate this German text into English: Hallo Welt!",
        }
    ],
}

response = requests.post(
    f"{BASE_URL}/chat/completions",
    headers=headers,
    json=payload,
    timeout=60,
)

print(response.status_code)
print(response.text)

if response.ok:
    print(response.json()["choices"][0]["message"]["content"].strip())
