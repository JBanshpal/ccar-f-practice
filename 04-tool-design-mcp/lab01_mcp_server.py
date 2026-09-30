"""One file, two roles:
  python lab01_mcp_server.py --serve     -> runs as an MCP server over stdio
  python lab01_mcp_server.py "prompt"    -> MCP client + Claude tool loop (spawns the server itself)
"""
import sys
import json
import asyncio
from dotenv import load_dotenv

# ---------------- server role ----------------
if "--serve" in sys.argv:
    from mcp.server.fastmcp import FastMCP

    mcp = FastMCP("orders")

    @mcp.tool()
    def get_order_status(order_id: str) -> dict:
        """Look up an order's shipping status by order ID. Use when the user asks where an order is."""
        if order_id != "A123":
            raise ValueError(f"Order {order_id} not found")
        return {"order_id": order_id, "status": "shipped", "eta": "2 days"}

    mcp.run()  # stdio transport by default; never print() to stdout here
    sys.exit(0)

# ---------------- client role ----------------
import anthropic
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

load_dotenv()
client = anthropic.Anthropic()
MAX_TURNS = 5


async def main(prompt):
    server = StdioServerParameters(command=sys.executable, args=[__file__, "--serve"])
    async with stdio_client(server) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            # Discover tools from the server instead of hardcoding them
            listed = await session.list_tools()
            tools = [
                {"name": t.name, "description": t.description, "input_schema": t.inputSchema}
                for t in listed.tools
            ]
            print("MCP tools discovered:", [t["name"] for t in tools])

            messages = [{"role": "user", "content": prompt}]
            for turn in range(1, MAX_TURNS + 1):
                resp = client.messages.create(
                    model="claude-sonnet-5-5", max_tokens=2000, tools=tools, messages=messages
                )
                print(f"[turn {turn}] stop_reason: {resp.stop_reason}  usage: {resp.usage}")
                messages.append({"role": "assistant", "content": resp.content})

                if resp.stop_reason != "tool_use":
                    print("".join(b.text for b in resp.content if b.type == "text"))
                    return

                results = []
                for block in resp.content:
                    if block.type != "tool_use":
                        continue
                    print(f"  -> Claude called {block.name} with {block.input}")
                    try:
                        out = await session.call_tool(block.name, block.input)
                        text = "".join(c.text for c in out.content if c.type == "text")
                        if out.isError:
                            print(f"  !! MCP tool error: {text}")
                        results.append({
                            "type": "tool_result",
                            "tool_use_id": block.id,
                            "content": text or json.dumps(out.structuredContent),
                            "is_error": bool(out.isError),
                        })
                    except Exception as e:  # transport/protocol failure, not a tool error
                        print(f"  !! MCP call failed: {e}")
                        results.append({
                            "type": "tool_result",
                            "tool_use_id": block.id,
                            "content": f"Error: {e}",
                            "is_error": True,
                        })
                messages.append({"role": "user", "content": results})
            print("Stopped: hit MAX_TURNS without a final answer.")


prompt = sys.argv[1] if len(sys.argv) > 1 else "Where are orders A123 and B999?"
print("PROMPT:", prompt)
asyncio.run(main(prompt))