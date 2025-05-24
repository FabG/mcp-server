# MCP-Server

This repo includes instruction and code to set up a MCP (Model Context Protocol) Server and add tools to it and interact with it with an LLM (Large Language Model).

### Intro about MCP
The Model Context Protocol (MCP) is a new, standardized way to provide context and tools to your LLMs. In this repo, we will use [FastMCP](https://gofastmcp.com/getting-started/welcome) which makes building MCP servers and clients simple and intuitive. 

[FastMCP 2.0](https://pypi.org/project/fastmcp/) is the #1 github trending repo, with over 10k stars and 600 forks as of May 2025.


Create tools, expose resources, define prompts, and more with clean, Pythonic code:
```python
from fastmcp import FastMCP

mcp = FastMCP("Demo 🚀")

@mcp.tool()
def add(a: int, b: int) -> int:
    """Add two numbers"""
    return a + b

if __name__ == "__main__":
    mcp.run()
```

#### What is MCP?

The Model Context Protocol lets you build servers that expose data and functionality to LLM applications in a secure, standardized way. It is often described as “the USB-C port for AI”, providing a uniform way to connect LLMs to resources they can use. It may be easier to think of it as an API, but specifically designed for LLM interactions.  
MCP servers can:
- Expose data through Resources (think of these sort of like GET endpoints; they are used to load information into the LLM’s context)
- Provide functionality through Tools (sort of like POST endpoints; they are used to execute code or otherwise produce a side effect)
- Define interaction patterns through Prompts (reusable templates for LLM interactions)
- And more!  
There is a low-level Python SDK available for implementing the protocol directly, but FastMCP aims to make that easier by providing a high-level, Pythonic interface.

#### Why FastMCP?
The MCP protocol is powerful but implementing it involves a lot of boilerplate - server setup, protocol handlers, content types, error management. FastMCP handles all the complex protocol details and server management, so you can focus on building great tools. It’s designed to be high-level and Pythonic; in most cases, decorating a function is all you need.

While the core server concepts of FastMCP 1.0 laid the groundwork and were contributed to the official MCP SDK, FastMCP 2.0 (this project) is the actively developed successor, adding significant enhancements and entirely new capabilities like a powerful client library, server proxying, composition patterns, and much more.

FastMCP aims to be:

🚀 Fast: High-level interface means less code and faster development

🍀 Simple: Build MCP servers with minimal boilerplate

🐍 Pythonic: Feels natural to Python developers

🔍 Complete: FastMCP aims to provide a full implementation of the core MCP specification


### Set up
We `uv` which, a rust package management tool, much faster than pip.
 If you don't have it already, install it:  
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

The advantages of `uv` over Pipenv/Pipfile include:

- Faster dependency resolution and installation times.
- Better integration with modern Python ecosystems like Poetry.
- Reduced overhead in virtual environment management.
- Enhanced security when resolving environment variables, though this also introduces new considerations (discussed later).

You may need to update your $PATH to reflex where uv gets installed.
Example for MacOS: `/Users/<user>/.local/bin/`

You can update your .bash_profile as follow:
```bash
# Setting PATH for uv
PATH="/Users/<user>/.local/bin/:${PATH}"
export PATH
```

Create a virtual environment
To create a default virtual env that will go in `.venv`, run:  
```bash
uv venv
```

Activate your environment
```bash
source .venv/bin/activate
```

Install the dependencies
```bash
uv add fastmcp==2.4.0 --frozen
```

Verify the version
```bash
fastmcp version
```

You should see something like that:
```bash
FastMCP version:                                                          2.4.0
MCP version:                                                              1.9.1
Python version:                                                          3.11.9
Platform:                                        macOS-15.4.1-x86_64-i386-64bit
FastMCP root path: /Users/Fab/Git/mcp-server/.venv/lib/python3.11/site-packages
```

### Usage 

```bash
uv run main.py
```
