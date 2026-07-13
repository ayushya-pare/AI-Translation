import os

import requests


API_KEY = os.getenv("API_KEY")
BASE_URL = os.getenv("BASE_URL", "https://openwebui-test.hrz.uni-bonn.de/api")

headers = {"Authorization": f"Bearer {API_KEY}"} if API_KEY else {}

response = requests.get(f"{BASE_URL}/models", headers=headers, timeout=30)
print(response.status_code)
print(response.text)
