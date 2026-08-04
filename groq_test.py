import os 
from groq import Groq
from dotenv import load_dotenv
load_dotenv()  # Load environment variables from .env file
api_key = os.environ.get("GROQ_API_KEY")
print(f"Using API Key: {api_key}")
client = Groq(api_key=api_key)
completion = client.chat.completions.create(
    model="llama-3.3-70b-versatile",
    messages=[
        {
            "role": "user",
            "content": "Write a python function to add two numbers"
        }
    ],
    temperature=0.7,
    max_tokens=100
)
print(completion.choices[0].message.content)