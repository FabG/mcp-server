# The FastMCP Server

The central piece of a FastMCP application is the `FastMCP` server class. This class acts as the main container for your application’s tools, resources, and prompts, and manages communication with MCP clients.

​
## Creating a Server

Instantiating a server is straightforward. You typically provide a name for your server, which helps identify it in client applications or logs.

```python
from fastmcp import FastMCP

# Create a basic server instance
mcp = FastMCP(name="MyAssistantServer")

# You can also add instructions for how to interact with the server
mcp_with_instructions = FastMCP(
    name="HelpfulAssistant",
    instructions="""
        This server provides data analysis tools.
        Call get_average() to analyze numerical data.
        """
)
```

The `FastMCP` constructor accepts several arguments:

 - `name`: (Optional) A human-readable name for your server. Defaults to “FastMCP”.
 - `instructions`: (Optional) Description of how to interact with this server. These instructions help clients understand the server’s purpose and available functionality.
 - `lifespan`: (Optional) An async context manager function for server startup and shutdown logic.
 - `tags`: (Optional) A set of strings to tag the server itself.
 - `**settings`: Keyword arguments corresponding to additional ServerSettings configuration


 ## Components
FastMCP servers expose several types of components to the client:

​
### Tools
Tools are functions that the client can call to perform actions or access external systems.
Creating a tool is as simple as decorating a Python function with `@mcp.tool()`:

```python
@mcp.tool()
def multiply(a: float, b: float) -> float:
    """Multiplies two numbers together."""
    return a * b
```
Tools are the core building blocks that allow your LLM to interact with external systems, execute code, and access data that isn’t in its training data. In FastMCP, tools are Python functions exposed to LLMs through the MCP protocol.

=> See [Tools FastMCP Documentation](https://gofastmcp.com/servers/tools) for more info

### Resources
Resources expose data sources that the client can read.

```python
@mcp.resource("data://config")
def get_config() -> dict:
    """Provides the application configuration."""
    return {"theme": "dark", "version": "1.0"}
```

Resources represent data or files that an MCP client can read, and resource templates extend this concept by allowing clients to request dynamically generated resources based on parameters passed in the URI.

=> See [Resources FastMCP Documentation](https://gofastmcp.com/servers/resources) for more info


### Resource Templates
Resource templates are parameterized resources that allow the client to request specific data.

```python
@mcp.resource("users://{user_id}/profile")
def get_user_profile(user_id: int) -> dict:
    """Retrieves a user's profile by ID."""
    # The {user_id} in the URI is extracted and passed to this function
    return {"id": user_id, "name": f"User {user_id}", "status": "active"}
```

### Prompts

Prompts are reusable message templates for guiding the LLM.
They help LLMs generate structured, purposeful responses. FastMCP simplifies defining these templates, primarily using the `@mcp.prompt` decorator:


```python
@mcp.prompt()
def analyze_data(data_points: list[float]) -> str:
    """Creates a prompt asking for analysis of numerical data."""
    formatted_data = ", ".join(str(point) for point in data_points)
    return f"Please analyze these data points: {formatted_data}"
```

Other example:
```python
from fastmcp import FastMCP
from fastmcp.prompts.prompt import Message, PromptMessage, TextContent

mcp = FastMCP(name="PromptServer")

# Basic prompt returning a string (converted to user message automatically)
@mcp.prompt()
def ask_about_topic(topic: str) -> str:
    """Generates a user message asking for an explanation of a topic."""
    return f"Can you please explain the concept of '{topic}'?"

# Prompt returning a specific message type
@mcp.prompt()
def generate_code_request(language: str, task_description: str) -> PromptMessage:
    """Generates a user message requesting code generation."""
    content = f"Write a {language} function that performs the following task: {task_description}"
    return PromptMessage(role="user", content=TextContent(type="text", text=content))
```


=> See [Prompts FastMCP Documentation](https://gofastmcp.com/servers/prompts) for more info



## Running the Server
FastMCP servers need a transport mechanism to communicate with clients. You typically start your server by calling the `mcp.run()` method on your FastMCP instance, often within an if`__name__ == "__main__":` block in your main server script. This pattern ensures compatibility with various MCP clients.

```python
# my_server.py
from fastmcp import FastMCP

mcp = FastMCP(name="MyServer")

@mcp.tool()
def greet(name: str) -> str:
    """Greet a user by name."""
    return f"Hello, {name}!"

if __name__ == "__main__":
    # This runs the server, defaulting to STDIO transport
    mcp.run()
    
    # To use a different transport, e.g., HTTP:
    # mcp.run(transport="streamable-http", host="127.0.0.1", port=9000)
```

FastMCP supports several transport options:

- STDIO (default, for local tools)
- Streamable HTTP (recommended for web services)
- SSE (legacy web transport, deprecated) 

The server can also be run using the FastMCP CLI.

For more infor, refer to [Running FastMCP Server documentation](https://gofastmcp.com/deployment/running-server)

## Authentication
FastMCP supports OAuth 2.0 authentication, allowing servers to protect their tools and resources. This is configured by providing an `auth_server_provider` and `auth settings` during FastMCP initialization.

```python
from fastmcp import FastMCP
from mcp.server.auth.settings import AuthSettings #, ... other auth imports
# from your_auth_implementation import MyOAuthServerProvider # Placeholder

# Create a server with authentication (conceptual example)
# mcp = FastMCP(
#     name="SecureApp",
#     auth_server_provider=MyOAuthServerProvider(),
#     auth=AuthSettings(
#         issuer_url="https://myapp.com",
#         # ... other OAuth settings ...
#         required_scopes=["myscope"],
#     ),
# )
```