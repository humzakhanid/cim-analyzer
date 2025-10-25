from openai import OpenAI
import os
from dotenv import load_dotenv

# Load your OpenAI API key from the .env file
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise RuntimeError("OPENAI_API_KEY not set.")

client = OpenAI(api_key=api_key)

# List all available models
models = client.models.list()

# Print model IDs
for model in models.data:
    print(model.id)
