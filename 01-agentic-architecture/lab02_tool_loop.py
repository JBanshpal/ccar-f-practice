from dotenv import load_dotenv
import anthropic, json
load_dotenv()
client = anthropic.Anthropic()

tools = [{
    "name": "get_order_status",
    "description": "Look up an order's shipping status by order ID. Use when the user asks where an order is.",
    "input_schema": {"type": "object",
                     "properties": {"order_id": {"type": "string"}},
                     "required": ["order_id"]},
}]

def get_order_status(order_id):  # fake backend
    return {"order_id": order_id, "status": "shipped", "eta": "2 days"}

messages = [{"role": "user", "content": "Where is order A123?"}]
while True:
    resp = client.messages.create(model="claude-sonnet-5-5", max_tokens=1000,
                                  tools=tools, messages=messages)
    messages.append({"role": "assistant", "content": resp.content})
    if resp.stop_reason != "tool_use":
        print(resp.content[0].text); break
    results = []
    for block in resp.content:
        if block.type == "tool_use":
            out = get_order_status(**block.input)
            results.append({"type": "tool_result", "tool_use_id": block.id,
                            "content": json.dumps(out)})
    messages.append({"role": "user", "content": results})