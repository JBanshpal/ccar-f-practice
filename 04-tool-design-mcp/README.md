# Lab 01: MCP server

## Goal
Move the `get_order_status` tool from lab02 (01-agentic-architecture) out of the agent and into an **MCP server**.
The client doesn't hardcode any tool definitions. It starts the server over stdio, finds the tools with
`list_tools()`, turns them into Claude tool definitions, and runs each `tool_use` through `call_tool()`.
The default prompt asks about one valid order and one invalid one, so you see a success and an
`is_error` result in the same run.

```
python lab01_mcp_server.py                      # default prompt
python lab01_mcp_server.py "Where is order A123?"
python lab01_mcp_server.py --serve              # server only (waits on stdin; Ctrl+C to quit)
```

## Exam domain and topic
Domain 4, Tool Design & MCP. Topics: the MCP client/server split, tool discovery, stdio transport,
and the difference between an MCP tool error (`isError`) and a transport failure.

## The tradeoff
**MCP server (tools found at runtime) vs. tools defined in the agent (lab02).**
- MCP: tools live in their own process. Any MCP host (Claude Code, Claude Desktop, this script) can reuse
  them, and they can change without redeploying the agent. The costs are an extra process, async code,
  another place for things to fail, and a model that only sees whatever descriptions the server publishes.
- Defined in the agent: simpler, faster, and easier to debug, but tied to one app. Pick this for a single
  agent with a few stable tools. Pick MCP when several clients share the tools, or another team owns them.

## Experiments
1. **Break the description.** Change the docstring to `"Does stuff."`. The model now sees that exact text
   as the tool description. Watch whether Claude still calls the tool, or asks you for clarification first.
2. **Pollute stdout.** Add `print("server starting")` inside the `--serve` branch before `mcp.run()`.
   stdio uses stdout as the protocol channel, so the client breaks during `initialize()`. Use stderr for logs.
3. **Set MAX_TURNS = 1** and ask about two orders one at a time (`"Check A123, then check B999"`).
   The loop stops with a message saying it hit MAX_TURNS. Then set `is_error` to always `False` and
   see whether Claude still tells the user the B999 lookup failed.