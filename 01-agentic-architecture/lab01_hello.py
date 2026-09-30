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
print(resp.content[0].text)
print(resp.usage)   # watch token counts — relevant to context management