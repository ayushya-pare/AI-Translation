import requests

import os


BASE_URL = os.getenv("BASE_URL", "https://openwebui-test.hrz.uni-bonn.de/api")
API_URL = f"{BASE_URL}/chat/completions"
API_KEY = os.getenv("API_KEY")
MODEL = os.getenv("MODEL_NAME", "local.openai/gpt-oss-120b")

if not API_KEY:
    raise SystemExit("Set API_KEY first.")

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}
data = {
    "model": MODEL,
    "messages": [
        {"role": "user", "content": "Hello world"}
    ]
}

response = requests.post(API_URL, headers=headers, json=data, timeout=60)
print(response.status_code)
print(response.text)
