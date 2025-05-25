# client.py - MCP client for interacting with the MCP server
#
# This client connects to the MCP server, lists available tools, and allows queries using OpenAI's API.
# It demonstrates how to use the server's web search and profile scraping tools programmatically.

import asyncio
import json
from contextlib import AsyncExitStack
from typing import Any, Dict, List

import nest_asyncio
from dotenv import load_dotenv
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from openai import AsyncOpenAI

# Apply nest_asyncio to allow nested event loops (needed for Jupyter/IPython)
# NOT needed for terminal usage
nest_asyncio.apply()

# Load environment variables from .env file
load_dotenv("../.env")

# Global variables to store session state (Must have OPEANI_API_KEY set in .env)
session = None
exit_stack = AsyncExitStack()
openai_client = AsyncOpenAI()
model = "gpt-4o"
stdio = None
write = None


async def connect_to_server(server_script_path: str = "server.py"):
    """Connect to an MCP server and list available tools."""
    global session, stdio, write, exit_stack

    # Server configuration
    server_params = StdioServerParameters(
        command="python",
        args=[server_script_path],
    )

    # Connect to the server using stdio transport
    stdio_transport = await exit_stack.enter_async_context(stdio_client(server_params))
    stdio, write = stdio_transport
    session = await exit_stack.enter_async_context(ClientSession(stdio, write))

    # Initialize the connection
    await session.initialize()

    # List available tools
    tools_result = await session.list_tools()
    print("\nConnected to server with tools:")
    for tool in tools_result.tools:
        print(f"  - {tool.name}: {tool.description}")


async def get_mcp_tools() -> List[Dict[str, Any]]:
    """Get available tools from the MCP server in OpenAI format."""
    global session

    tools_result = await session.list_tools()
    return [
        {
            "type": "function",
            "function": {
                "name": tool.name,
                "description": tool.description,
                "parameters": tool.inputSchema,
            },
        }
        for tool in tools_result.tools
    ]


async def process_query(query: str) -> str:
    """Send a query to the OpenAI API, using MCP tools as needed."""
    global session, openai_client, model

    tools = await get_mcp_tools()
    messages = [{"role": "user", "content": query}]

    while True:
        # Send the user query to OpenAI's chat API, with available tools
        response = await openai_client.chat.completions.create(
            model=model,
            messages=messages,
            tools=tools,
            tool_choice="auto",
        )
        assistant_message = response.choices[0].message
        messages.append(assistant_message)


        # If the assistant does not call a tool, return the response
        if not assistant_message.tool_calls:
            return assistant_message.content

        # If a tool is called, execute it and append the result
        for tool_call in assistant_message.tool_calls:
            result = await session.call_tool(
                tool_call.function.name,
                arguments=json.loads(tool_call.function.arguments),
            )
            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": result.content[0].text,
            })
            print(f"\nresult: {result.content[0].text}")
            

async def cleanup():
    """Clean up resources and close connections."""
    global exit_stack
    await exit_stack.aclose()


async def main():
    """Main entry point for the client. Connects to the server and processes a sample query."""
    await connect_to_server("server_amazon_scraper.py")
    query = "Extract all available product data from this Amazon URL: https://www.amazon.com/dp/B09C13PZX7. Format the output as a structured JSON object."
    print(f"\nQuery: {query}")

    response = await process_query(query)
    print(f"\nResponse: {response}")
    await cleanup()

if __name__ == "__main__":
    asyncio.run(main())