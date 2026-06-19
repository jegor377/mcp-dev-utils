"""
Quick manual test client for the dev-utils MCP server.
Run with: uv run python test_client.py
"""

import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def main():
    server = StdioServerParameters(command="uv", args=["run", "python", "server.py"])

    async with stdio_client(server) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            # List all available tools
            tools = await session.list_tools()
            print("=== Available tools ===")
            for tool in tools.tools:
                print(f"  - {tool.name}: {tool.description}")

            print()

            # Call each tool with example inputs
            print("=== format_json ===")
            r = await session.call_tool("format_json", {"json_string": '{"hello":"world","n":42}'})
            print(r.content[0].text)

            print("=== generate_uuid ===")
            r = await session.call_tool("generate_uuid", {"count": 3})
            print(r.content[0].text)

            print("=== base64_convert (encode) ===")
            r = await session.call_tool("base64_convert", {"text": "hello MCP", "mode": "encode"})
            print(r.content[0].text)

            print("=== http_status ===")
            r = await session.call_tool("http_status", {"code": 404})
            print(r.content[0].text)

            print("=== unix_timestamp (now) ===")
            r = await session.call_tool("unix_timestamp", {})
            print(r.content[0].text)


asyncio.run(main())
