"""
Minimal MCP client for manually sanity-checking the testbed server.

Run the server in one terminal:
    python -m server.testbed_server

This script isn't needed for the corpus/detection pipeline (that's fully
synthetic) - it's here so you can actually see a real MCP tool-call
round-trip happen, for demos or for your supervisor.

Usage:
    python -m client.testbed_client
"""

import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def main():
    server_params = StdioServerParameters(
        command="python3",
        args=["-m", "server.testbed_server"],
    )
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            tools = await session.list_tools()
            print("Tools exposed by server:")
            for t in tools.tools:
                print(f"  - {t.name}: {t.description}")

            result = await session.call_tool("get_weather", {"city": "Preston", "units": "metric"})
            print("\nCalled get_weather ->")
            print(result.content)


if __name__ == "__main__":
    asyncio.run(main())
