import csv
import os
import random
from pathlib import Path

import requests

test_set = Path("data/outputs/test_set.csv")

with test_set.open(encoding="utf-8") as file:
    row = random.choice(list(csv.DictReader(file)))

german_text = row["de_text"]
ground_truth = row["en_grtr"]

prompts = [
    """Act as a professional German-to-English translator. 
    Write a natural English version of this German text. 
    Output only the translated text. 
    Do not add Markdown, comments or explanations. """
]

url = os.getenv(
    "BASE_URL",
    "https://openwebui-test.hrz.uni-bonn.de/api",
) + "/chat/completions"

model = os.getenv("MODEL_NAME", "local.openai/gpt-oss-120b")

print("\nGerman text:")
print(german_text)
print("\nGround-truth translation:")
print(ground_truth)

for number, prompt in enumerate(prompts, start=1):
    response = requests.post(
        url,
        headers={
            "Authorization": f"Bearer {os.environ['API_KEY']}",
            "Content-Type": "application/json",
        },
        json={
            "model": model,
            "messages": [
                {
                    "role": "user",
                    "content": f"{prompt}\n\nGerman:\n{german_text}\n\nEnglish:",
                }
            ],
            "temperature": 0,
        },
        timeout=60,
    )
    response.raise_for_status()
    translation = response.json()["choices"][0]["message"]["content"].strip()

    #print(prompt)
    print("\nLLM translation:")
    print(translation)