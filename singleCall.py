from pathlib import Path
import os

from dotenv import load_dotenv
from ollama import chat


load_dotenv(Path(__file__).with_name(".env"))

MODEL_NAME = os.getenv("OLLAMA_MODEL", "qwen3:latest").strip()
think_setting = os.getenv("OLLAMA_THINK", "true").strip().lower()

if not MODEL_NAME:
    raise ValueError("OLLAMA_MODEL in .env must not be empty")
if think_setting not in {"true", "false"}:
    raise ValueError("OLLAMA_THINK in .env must be true or false")

THINK = think_setting == "true"


def get_temperature(city: str) -> str:
    """Get the current temperature for a city from sample data."""
    temperatures = {
        "New York": "22°C",
        "London": "15°C",
        "Tokyo": "18°C",
    }
    return temperatures.get(city, "Unknown")


messages = [{"role": "user", "content": "What is the temperature in Tokyo?"}]

# Pass the function directly as an Ollama tool.
response = chat(
    model=MODEL_NAME,
    messages=messages,
    tools=[get_temperature],
    think=THINK,
)

messages.append(response.message)
if response.message.tool_calls:
    # Run every tool call the model requested, such as one call per city.
    for call in response.message.tool_calls:
        print(f"Tool call: {call.function.name}({call.function.arguments})")
        result = get_temperature(**call.function.arguments)
        print(f"Tool result: {result}")
        messages.append(
            {"role": "tool", "tool_name": call.function.name, "content": str(result)}
        )

    final_response = chat(
        model=MODEL_NAME,
        messages=messages,
        tools=[get_temperature],
        think=THINK,
    )
    print(final_response.message.content)
else:
    print(response.message.content)
