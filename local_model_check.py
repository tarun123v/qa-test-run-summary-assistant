from ollama import chat

response = chat(
    model="llama3.2:latest",
    messages=[{"role": "user", "content": "Reply with LOCAL MODEL READY"}],
)
print(response.message.content);
