"""Setup script for the YouTube to LinkedIn MCP server."""
from setuptools import find_packages, setup

setup(
    name="yt-to-linkedin-mcp",
    version="0.1.0",
    description="Model Context Protocol server that automates generating LinkedIn post drafts from YouTube videos",
    author="Anirudh Nuti",
    author_email="your-email@example.com",
    packages=find_packages(),
    install_requires=[
        "fastapi>=0.95.0",
        "uvicorn>=0.21.1",
        "openai>=0.27.0",
        "youtube-transcript-api>=0.6.0",
        "httpx>=0.24.0",
        "typer>=0.9.0",
        "mcp>=0.1.0",
        "pydantic>=2.0.0",
    ],
    entry_points={
        "console_scripts": [
            "yt-to-linkedin-mcp=yt_to_linkedin_mcp:app",
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.9",
)
