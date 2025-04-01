from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
import logging
import os
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
        "tools": [
            {
                "name": "extract_transcript",
                "description": "Extract transcript from a YouTube video",
                "parameters": {
                    "youtube_url": "URL of the YouTube video",
                    "language": "Language code for the transcript (default: en)"
                }
            },
            {
                "name": "generate_summary",
                "description": "Generate a summary from a video transcript",
                "parameters": {
                    "transcript": "Video transcript text",
                    "video_title": "Title of the video",
                    "tone": "Tone of the summary",
                    "audience": "Target audience",
                    "max_length": "Maximum summary length in words",
                    "min_length": "Minimum summary length in words"
                }
            },
            {
                "name": "generate_post",
                "description": "Generate a LinkedIn post from a video summary",
                "parameters": {
                    "summary": "Video summary",
                    "video_title": "Title of the video",
                    "video_url": "URL of the YouTube video",
                    "speaker_name": "Name of the speaker in the video (optional)",
                    "hashtags": "List of hashtags to include (optional)",
                    "tone": "Tone of the post",
                    "voice": "Voice of the post",
                    "audience": "Target audience",
                    "include_call_to_action": "Whether to include a call to action",
                    "max_length": "Maximum post length in characters"
                }
            },
            {
                "name": "format_output",
                "description": "Format the LinkedIn post for output",
                "parameters": {
                    "post_content": "LinkedIn post content",
                    "format": "Output format (json, text, markdown, html)"
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
