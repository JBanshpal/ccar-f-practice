from dotenv import load_dotenv
import anthropic, json

load_dotenv()
client = anthropic.Anthropic()

tools = [{
    "name": "get_order_status",
    "description": "Look up an order's shipping status by order ID. Use when the user asks where an order is.",
    "input_schema": {
        "type": "object",
        "properties": {"order_id": {"type": "string"}},
        "required": ["order_id"],
    },
}]

def get_order_status(order_id):  # fake backend
    return {"order_id": order_id, "status": "shipped", "eta": "2 days"}

messages = [{"role": "user", "content": "Where is order A123?"}]
MAX_TURNS = 5

for turn in range(1, MAX_TURNS + 1):
    resp = client.messages.create(
        model="claude-sonnet-5-5", max_tokens=2000, tools=tools, messages=messages
    )
    print(f"[turn {turn}] stop_reason: {resp.stop_reason}")
    messages.append({"role": "assistant", "content": resp.content})

    if resp.stop_reason != "tool_use":
        print("".join(b.text for b in resp.content if b.type == "text"))
        break

    results = []
    for block in resp.content:
        if block.type == "tool_use":
            print(f"  -> Claude called {block.name} with {block.input}")
            out = get_order_status(**block.input)
            results.append({
                "type": "tool_result",
                "tool_use_id": block.id,
                "content": json.dumps(out),
            })
    messages.append({"role": "user", "content": results})
else:
    print("Stopped: hit MAX_TURNS without a final answer.")