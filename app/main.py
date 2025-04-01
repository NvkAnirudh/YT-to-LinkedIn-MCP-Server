from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
import logging
from dotenv import load_dotenv

from app.routers import transcript, summary, post_generation, output

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="YouTube to LinkedIn MCP Server",
    description="Model Context Protocol server for generating LinkedIn posts from YouTube videos",
    version="1.0.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(transcript.router, prefix="/api/v1", tags=["Transcript"])
app.include_router(summary.router, prefix="/api/v1", tags=["Summary"])
app.include_router(post_generation.router, prefix="/api/v1", tags=["Post Generation"])
app.include_router(output.router, prefix="/api/v1", tags=["Output"])

# Tool listing endpoint for Smithery
@app.get("/list-tools")
async def list_tools():
    """
    List available tools for Smithery integration.
    This endpoint does not require authentication.
    """
    return {
        "schema_version": "v1",
        "name_for_human": "YouTube to LinkedIn MCP Server",
        "name_for_model": "youtube_to_linkedin",
        "description_for_human": "Generate LinkedIn posts from YouTube videos",
        "description_for_model": "This service extracts transcripts from YouTube videos, summarizes them, and generates LinkedIn posts.",
        "auth": {
            "type": "none"
        },
        "api": {
            "type": "openapi",
            "url": "/openapi.json"
        },
        "tools": [
            {
                "type": "function",
                "function": {
                    "name": "extract_transcript",
                    "description": "Extract transcript from a YouTube video",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "youtube_url": {
                                "type": "string",
                                "description": "URL of the YouTube video"
                            },
                            "language": {
                                "type": "string",
                                "description": "Language code for the transcript (default: en)"
                            },
                            "youtube_api_key": {
                                "type": "string",
                                "description": "Optional YouTube Data API key"
                            }
                        },
                        "required": ["youtube_url"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "generate_summary",
                    "description": "Generate a summary from a video transcript",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "transcript": {
                                "type": "string",
                                "description": "Video transcript text"
                            },
                            "video_title": {
                                "type": "string",
                                "description": "Title of the video"
                            },
                            "tone": {
                                "type": "string",
                                "description": "Tone of the summary",
                                "enum": ["educational", "inspirational", "professional", "conversational", "thought_leader"]
                            },
                            "audience": {
                                "type": "string",
                                "description": "Target audience",
                                "enum": ["general", "technical", "executive", "entry_level", "industry_specific"]
                            },
                            "max_length": {
                                "type": "integer",
                                "description": "Maximum summary length in words"
                            },
                            "min_length": {
                                "type": "integer",
                                "description": "Minimum summary length in words"
                            },
                            "openai_api_key": {
                                "type": "string",
                                "description": "Optional OpenAI API key"
                            }
                        },
                        "required": ["transcript", "video_title", "tone", "audience"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "generate_post",
                    "description": "Generate a LinkedIn post from a video summary",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "summary": {
                                "type": "string",
                                "description": "Video summary"
                            },
                            "video_title": {
                                "type": "string",
                                "description": "Title of the video"
                            },
                            "video_url": {
                                "type": "string",
                                "description": "URL of the YouTube video"
                            },
                            "speaker_name": {
                                "type": "string",
                                "description": "Name of the speaker in the video (optional)"
                            },
                            "hashtags": {
                                "type": "array",
                                "items": {
                                    "type": "string"
                                },
                                "description": "List of hashtags to include (optional)"
                            },
                            "tone": {
                                "type": "string",
                                "description": "Tone of the post",
                                "enum": ["educational", "inspirational", "professional", "conversational", "thought_leader"]
                            },
                            "voice": {
                                "type": "string",
                                "description": "Voice of the post",
                                "enum": ["first_person", "third_person"]
                            },
                            "audience": {
                                "type": "string",
                                "description": "Target audience",
                                "enum": ["general", "technical", "executive", "entry_level", "industry_specific"]
                            },
                            "include_call_to_action": {
                                "type": "boolean",
                                "description": "Whether to include a call to action"
                            },
                            "max_length": {
                                "type": "integer",
                                "description": "Maximum post length in characters"
                            },
                            "openai_api_key": {
                                "type": "string",
                                "description": "Optional OpenAI API key"
                            }
                        },
                        "required": ["summary", "video_title", "video_url", "tone", "voice", "audience"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "format_output",
                    "description": "Format the LinkedIn post for output",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "post_content": {
                                "type": "string",
                                "description": "LinkedIn post content"
                            },
                            "format": {
                                "type": "string",
                                "description": "Output format",
                                "enum": ["json", "text", "markdown", "html"]
                            }
                        },
                        "required": ["post_content", "format"]
                    }
                }
            }
        ]
    }

# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "YouTube to LinkedIn MCP Server",
        "docs": "/docs",
        "version": "1.0.0",
    }

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy"}

# Custom OpenAPI schema
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
