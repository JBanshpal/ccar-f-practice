from dotenv import load_dotenv
import anthropic

load_dotenv()
client = anthropic.Anthropic()

resp = client.messages.create(
    model="claude-sonnet-5-5",
    max_tokens=500,
    system="You are a concise solutions architect.",
    messages=[{"role": "user", "content": "When should I use a multi-agent design vs a single agent?"}],
)

for block in resp.content:
    if block.type == "thinking":
        print("--- THINKING ---\n", block.thinking)
    elif block.type == "text":
        print("--- ANSWER ---\n", block.text)

print(resp.usage)