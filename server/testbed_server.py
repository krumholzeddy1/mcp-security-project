"""
Local MCP server harness (Deliverable 1: "MCP testbed setup").

Run with:
    python -m server.testbed_server

This exposes the benign tool catalog over MCP using stdio transport, so it
can be pointed at from any MCP-compatible client (Claude Desktop, the MCP
Inspector, or the simple client in client/testbed_client.py) for manual
sanity-checking. The corpus generator in corpus/generate_corpus.py does NOT
go through this live server — it synthesizes metadata directly, which is
what the anomaly detector actually trains on. This server is here so you
can demo/inspect real MCP behaviour, not so the whole pipeline depends on it.
"""

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("testbed-server")


@mcp.tool(description="Returns the current weather for a given city name.")
def get_weather(city: str, units: str = "metric") -> str:
    return f"[get_weather] ok - city={city}, units={units}"


@mcp.tool(description="Searches an internal document index and returns matching titles.")
def search_docs(query: str, max_results: int = 5) -> str:
    return f"[search_docs] ok - query={query}, max_results={max_results}"


@mcp.tool(description="Creates a support ticket with a title and description.")
def create_ticket(title: str, description: str, priority: str = "normal") -> str:
    return f"[create_ticket] ok - title={title}, priority={priority}"


@mcp.tool(description="Sends a notification message to a named channel.")
def send_notification(channel: str, message: str) -> str:
    return f"[send_notification] ok - channel={channel}"


@mcp.tool(description="Looks up a customer account record by account ID.")
def lookup_account(account_id: str) -> str:
    return f"[lookup_account] ok - account_id={account_id}"

if __name__ == "__main__":
    mcp.run()
