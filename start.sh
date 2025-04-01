#!/bin/bash
set -e

# Load environment variables from .env file if it exists
if [ -f .env ]; then
    echo "Loading environment variables from .env file"
    export $(grep -v '^#' .env | xargs)
fi

# Check for required environment variables
if [ -z "$OPENAI_API_KEY" ]; then
    echo "Warning: OPENAI_API_KEY is not set. Summarization and post generation will not work."
fi

if [ -z "$YOUTUBE_API_KEY" ]; then
    echo "Warning: YOUTUBE_API_KEY is not set. Some video metadata features will be limited."
fi

# Start the application with uvicorn
echo "Starting YouTube to LinkedIn MCP server..."
exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000} ${RELOAD:+--reload}
