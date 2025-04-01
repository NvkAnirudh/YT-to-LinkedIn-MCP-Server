"""MCP server implementation for YouTube to LinkedIn."""
import logging
import typing as t
from typing import Any, Dict, List, Sequence

from mcp.content import EmbeddedResource, ImageContent, TextContent
from mcp.server.app import App

from .tools import TOOLS, TOOL_MAP, tool_args, tool_runner

logger = logging.getLogger(__name__)

app = App()


@app.list_tools()
async def list_tools() -> List[Dict[str, Any]]:
    """List available tools."""
    return [
        {
            "type": "function",
            "function": {
                "name": tool.name,
                "description": tool.description,
                "parameters": {
                    "type": "object",
                    "properties": {
                        arg.name: {
                            "type": str(arg.type.__name__),
                            "description": arg.description,
                        }
                        for arg in tool.args
                    },
                    "required": [arg.name for arg in tool.args if arg.required],
                },
            },
        }
        for tool in TOOLS
    ]


@app.progress_notification()
async def progress_notification(progress: str | int, p: float, s: float | None) -> None:
    """Progress notification."""
    # This is just a placeholder implementation
    pass


@app.call_tool()
async def call_tool(name: str, arguments: t.Any) -> Sequence[TextContent | ImageContent | EmbeddedResource]:
    """Handle tool calls for command line run."""
    if not isinstance(arguments, dict):
        raise TypeError("arguments must be dictionary")

    tool = TOOL_MAP.get(name)
    if not tool:
        raise ValueError(f"Unknown tool: {name}")

    try:
        # Add the tool name to the arguments so the tool_runner knows which tool to run
        arguments["tool_name"] = name
        args = tool_args(tool, **arguments)
        return await tool_runner(args)
    except Exception as e:
        logger.exception("Error running tool: %s", name)
        raise RuntimeError(f"Caught Exception. Error: {e}") from e


async def run_mcp_server() -> None:
    """Run the MCP server."""
    # Import here to avoid issues with event loops
    from mcp.server.stdio import stdio_server
    import asyncio

    async with stdio_server() as (read_stream, write_stream):
        session = await app.create_session(read_stream, write_stream)
        await session.run()
