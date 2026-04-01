from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()

api_key = os.getenv("NVIDIA_API_KEY")
print(f"🔑 Key found: {api_key[:12]}..." if api_key else "❌ No key found!")

client = OpenAI(
    base_url="https://integrate.api.nvidia.com/v1",
    api_key=api_key,
)

print("🔌 Testing connection to NVIDIA NIM...")

try:
    response = client.chat.completions.create(
        model="nvidia/nemotron-3-super-120b-a12b",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Say hello in one sentence."},
        ],
        temperature=0.7,
        max_tokens=50,
    )
    print(f"✅ SUCCESS! Response: {response.choices[0].message.content}")
    print(f"📊 Tokens used: {response.usage.total_tokens}")
except Exception as e:
    print(f"❌ ERROR: {e}")