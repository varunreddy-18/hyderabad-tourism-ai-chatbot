import os
from dotenv import load_dotenv
from huggingface_hub import InferenceClient

load_dotenv()


class HuggingFaceLLM:
    def __init__(self):
        self.client = InferenceClient(
            api_key=os.getenv("HF_TOKEN")
        )

    def generate(self, prompt):

        response = self.client.chat.completions.create(
            model="mistralai/Mistral-7B-Instruct-v0.3",
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            max_tokens=300
        )

        return response.choices[0].message.content