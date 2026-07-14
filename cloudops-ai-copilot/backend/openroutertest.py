from openrouter import OpenRouter
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

api_key = os.getenv("OPENROUTER_API_KEY")
if not api_key:
    raise ValueError(
        "Error: OPENROUTER_API_KEY is not set. Please add it to your backend/.env file "
        "or set it in your terminal environment variables."
    )

with OpenRouter(api_key=api_key) as client:
    response = client.chat.send(
        model="openai/gpt-4o-mini",
        messages=[
            {"role": "user", "content": "What is the meaning of life?"}
        ],
    )

    print(response.choices[0].message.content)