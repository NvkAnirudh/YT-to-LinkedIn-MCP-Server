"""Tools for the YouTube to LinkedIn MCP server."""
import json
import logging
import typing as t
from dataclasses import dataclass
from typing import Any, Dict, List, Sequence, Union

from mcp.content import EmbeddedResource, ImageContent, TextContent

logger = logging.getLogger(__name__)


@dataclass
class ToolArg:
    """Tool argument."""

    name: str
    type: t.Any
    description: str
    required: bool = True
    default: t.Any = None


@dataclass
class Tool:
    """Tool definition."""

    name: str
    description: str
    args: List[ToolArg]


# Define the tools for our YouTube to LinkedIn MCP server
TOOLS = [
    Tool(
        name="extract_transcript",
        description="Extract transcript from a YouTube video",
        args=[
            ToolArg(
                name="youtube_url",
                type=str,
                description="URL of the YouTube video",
                required=True,
            ),
            ToolArg(
                name="language",
                type=str,
                description="Language code for the transcript (default: en)",
                required=False,
                default="en",
            ),
            ToolArg(
                name="youtube_api_key",
                type=str,
                description="Optional YouTube Data API key",
                required=False,
                default=None,
            ),
        ],
    ),
    Tool(
        name="generate_summary",
        description="Generate a summary from a video transcript",
        args=[
            ToolArg(
                name="transcript",
                type=str,
                description="Video transcript text",
                required=True,
            ),
            ToolArg(
                name="video_title",
                type=str,
                description="Title of the video",
                required=True,
            ),
            ToolArg(
                name="tone",
                type=str,
                description="Tone of the summary",
                required=True,
            ),
            ToolArg(
                name="audience",
                type=str,
                description="Target audience",
                required=True,
            ),
            ToolArg(
                name="max_length",
                type=int,
                description="Maximum summary length in words",
                required=False,
                default=250,
            ),
            ToolArg(
                name="min_length",
                type=int,
                description="Minimum summary length in words",
                required=False,
                default=150,
            ),
            ToolArg(
                name="openai_api_key",
                type=str,
                description="Optional OpenAI API key",
                required=False,
                default=None,
            ),
        ],
    ),
    Tool(
        name="generate_post",
        description="Generate a LinkedIn post from a video summary",
        args=[
            ToolArg(
                name="summary",
                type=str,
                description="Video summary",
                required=True,
            ),
            ToolArg(
                name="video_title",
                type=str,
                description="Title of the video",
                required=True,
            ),
            ToolArg(
                name="video_url",
                type=str,
                description="URL of the YouTube video",
                required=True,
            ),
            ToolArg(
                name="tone",
                type=str,
                description="Tone of the post",
                required=True,
            ),
            ToolArg(
                name="voice",
                type=str,
                description="Voice of the post",
                required=True,
            ),
            ToolArg(
                name="audience",
                type=str,
                description="Target audience",
                required=True,
            ),
            ToolArg(
                name="speaker_name",
                type=str,
                description="Name of the speaker in the video (optional)",
                required=False,
                default=None,
            ),
            ToolArg(
                name="hashtags",
                type=list,
                description="List of hashtags to include (optional)",
                required=False,
                default=[],
            ),
            ToolArg(
                name="include_call_to_action",
                type=bool,
                description="Whether to include a call to action",
                required=False,
                default=True,
            ),
            ToolArg(
                name="max_length",
                type=int,
                description="Maximum post length in characters",
                required=False,
                default=1200,
            ),
            ToolArg(
                name="openai_api_key",
                type=str,
                description="Optional OpenAI API key",
                required=False,
                default=None,
            ),
        ],
    ),
    Tool(
        name="format_output",
        description="Format the LinkedIn post for output",
        args=[
            ToolArg(
                name="post_content",
                type=str,
                description="LinkedIn post content",
                required=True,
            ),
            ToolArg(
                name="format",
                type=str,
                description="Output format (json, text, markdown, html)",
                required=True,
            ),
        ],
    ),
]

# Create a mapping of tool names to tool objects
TOOL_MAP = {tool.name: tool for tool in TOOLS}


def tool_args(tool: Tool, **kwargs: Any) -> Dict[str, Any]:
    """Process tool arguments."""
    result = {}
    for arg in tool.args:
        if arg.name in kwargs:
            result[arg.name] = kwargs[arg.name]
        elif arg.required:
            raise ValueError(f"Missing required argument: {arg.name}")
        elif arg.default is not None:
            result[arg.name] = arg.default
    return result


async def tool_runner(args: Dict[str, Any]) -> Sequence[Union[TextContent, ImageContent, EmbeddedResource]]:
    """Run the appropriate tool based on the arguments."""
    # This would normally call your actual API endpoints
    # For now, we'll just return a mock response
    import httpx
    
    # Extract the tool name from the args
    tool_name = args.get("tool_name")
    
    if tool_name == "extract_transcript":
        # Call your existing transcript API
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "http://localhost:8000/api/v1/transcript",
                json={
                    "youtube_url": args["youtube_url"],
                    "language": args.get("language", "en"),
                    "youtube_api_key": args.get("youtube_api_key"),
                }
            )
            result = response.json()
    
    elif tool_name == "generate_summary":
        # Call your existing summary API
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "http://localhost:8000/api/v1/summarize",
                json={
                    "transcript": args["transcript"],
                    "video_title": args["video_title"],
                    "tone": args["tone"],
                    "audience": args["audience"],
                    "max_length": args.get("max_length", 250),
                    "min_length": args.get("min_length", 150),
                    "openai_api_key": args.get("openai_api_key"),
                }
            )
            result = response.json()
    
    elif tool_name == "generate_post":
        # Call your existing post generation API
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "http://localhost:8000/api/v1/generate-post",
                json={
                    "summary": args["summary"],
                    "video_title": args["video_title"],
                    "video_url": args["video_url"],
                    "tone": args["tone"],
                    "voice": args["voice"],
                    "audience": args["audience"],
                    "speaker_name": args.get("speaker_name"),
                    "hashtags": args.get("hashtags", []),
                    "include_call_to_action": args.get("include_call_to_action", True),
                    "max_length": args.get("max_length", 1200),
                    "openai_api_key": args.get("openai_api_key"),
                }
            )
            result = response.json()
    
    elif tool_name == "format_output":
        # Call your existing output API
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "http://localhost:8000/api/v1/output",
                json={
                    "post_content": args["post_content"],
                    "format": args["format"],
                }
            )
            result = response.json()
    
    else:
        result = {"error": f"Unknown tool: {tool_name}"}
    
    # Return the result as TextContent
    return [TextContent(json.dumps(result, indent=2))]
