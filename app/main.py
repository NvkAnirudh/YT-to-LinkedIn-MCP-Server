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
