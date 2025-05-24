
# Creating a FastMCP Server and Tools

### Creating a FastMCP Server
A FastMCP server is a collection of tools, resources, and other MCP components. To create a server, start by instantiating the FastMCP class.

Create a new file called my_server.py and add the following code:
```python
from fastmcp import FastMCP

mcp = FastMCP("My MCP Server")
```
That’s it! You’ve created a FastMCP server, albeit a very boring one. Let’s add a tool to make it more interesting.

### Adding a Tool
To add a tool that returns a simple greeting, write a function and decorate it with @mcp.tool to register it with the server:
```python
from fastmcp import FastMCP

mcp = FastMCP("My MCP Server")

@mcp.tool()
def greet(name: str) -> str:
    return f"Hello, {name}!"
```

### Testing the Server
To test the server, create a FastMCP client and point it at the server object.


```python
import asyncio
from fastmcp import FastMCP, Client

mcp = FastMCP("My MCP Server")

@mcp.tool()
def greet(name: str) -> str:
    return f"Hello, {name}!"

client = Client(mcp)

async def call_tool(name: str):
    async with client:
        result = await client.call_tool("greet", {"name": name})
        print(result)

asyncio.run(call_tool("Ford"))
```
There are a few things to note here:

- Clients are asynchronous, so we need to use `asyncio.run` to run the client.
` We must enter a client context (`async with client:`) before using the client. You can make multiple client calls within the same context.
​
### Running the server
In order to run the server with Python, we need to add a `run` statement to the `__main__` block of the server file.
```python
from fastmcp import FastMCP

mcp = FastMCP("My MCP Server")

@mcp.tool()
def greet(name: str) -> str:
    return f"Hello, {name}!"

if __name__ == "__main__":
    mcp.run()
```

This lets us run the server with `python my_server.py`, using the default `stdio` transport, which is the standard way to expose an MCP server to a client.

```bash
$ python3 my_server.py
[05/24/25 14:45:44] INFO     Starting MCP server 'My MCP Server' with transport 'stdio'
```

### Interacting with the Python server
Now that the server can be executed with `python my_server.py`, we can interact with it like any other MCP server.

In a new file, create a client and point it at the server file:
```python
import asyncio
from fastmcp import Client

client = Client("my_server.py")

async def call_tool(name: str):
    async with client:
        result = await client.call_tool("greet", {"name": name})
        print(result)

asyncio.run(call_tool("Ford"))
```
Example:
```bash
$ python3 my_client.py
[05/24/25 14:45:55] INFO     Starting MCP server 'My MCP Server' with transport 'stdio'                                 server.py:747
[TextContent(type='text', text='Hello, Ford!', annotations=None)]
```

### Using the FastMCP CLI
To have FastMCP run the server for us, we can use the `fastmcp run` command.  
This will start the server and keep it running until it is stopped. By default, it will use the `stdio` transport, which is a simple text-based protocol for interacting with the server.
```bash
fastmcp run my_server.py:mcp
```

Example:
```bash
fastmcp run my_server.py:mcp
[05/24/25 14:47:48] INFO     Starting MCP server 'My MCP Server' with transport 'stdio'                                       server.py:747
```