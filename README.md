# YouTube to LinkedIn MCP Server

A Model Context Protocol (MCP) server that automates generating LinkedIn post drafts from YouTube videos. This server provides high-quality, editable content drafts based on YouTube video transcripts.

## Features

- **YouTube Transcript Extraction**: Extract transcripts from YouTube videos using video URLs
- **Transcript Summarization**: Generate concise summaries of video content using OpenAI GPT
- **LinkedIn Post Generation**: Create professional LinkedIn post drafts with customizable tone and style
- **Modular API Design**: Clean FastAPI implementation with well-defined endpoints
- **Containerized Deployment**: Ready for deployment on Smithery

## Setup Instructions

### Prerequisites

- Python 3.8+
- Docker (for containerized deployment)
- OpenAI API Key
- YouTube Data API Key (optional, but recommended for better metadata)

### Local Development

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd yt-to-linkedin
   ```

2. Create a virtual environment and install dependencies:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. Create a `.env` file in the project root with your API keys:
   ```
   OPENAI_API_KEY=your_openai_api_key
   YOUTUBE_API_KEY=your_youtube_api_key
   ```

4. Run the application:
   ```bash
   uvicorn app.main:app --reload
   ```

5. Access the API documentation at http://localhost:8000/docs

### Docker Deployment

1. Build the Docker image:
   ```bash
   docker build -t yt-to-linkedin-mcp .
   ```

2. Run the container:
   ```bash
   docker run -p 8000:8000 --env-file .env yt-to-linkedin-mcp
   ```

### Smithery Deployment

1. Ensure you have the Smithery CLI installed and configured.

2. Deploy to Smithery:
   ```bash
   smithery deploy
   ```

## API Endpoints

### 1. Transcript Extraction

**Endpoint**: `/api/v1/transcript`  
**Method**: POST  
**Description**: Extract transcript from a YouTube video

**Request Body**:
```json
{
  "youtube_url": "https://www.youtube.com/watch?v=VIDEO_ID",
  "language": "en",
  "youtube_api_key": "your_youtube_api_key"  // Optional, provide your own YouTube API key
}
```

**Response**:
```json
{
  "video_id": "VIDEO_ID",
  "video_title": "Video Title",
  "transcript": "Full transcript text...",
  "language": "en",
  "duration_seconds": 600,
  "channel_name": "Channel Name",
  "error": null
}
```

### 2. Transcript Summarization

**Endpoint**: `/api/v1/summarize`  
**Method**: POST  
**Description**: Generate a summary from a video transcript

**Request Body**:
```json
{
  "transcript": "Video transcript text...",
  "video_title": "Video Title",
  "tone": "professional",
  "audience": "general",
  "max_length": 250,
  "min_length": 150,
  "openai_api_key": "your_openai_api_key"  // Optional, provide your own OpenAI API key
}
```

**Response**:
```json
{
  "summary": "Generated summary text...",
  "word_count": 200,
  "key_points": [
    "Key point 1",
    "Key point 2",
    "Key point 3"
  ]
}
```

### 3. LinkedIn Post Generation

**Endpoint**: `/api/v1/generate-post`  
**Method**: POST  
**Description**: Generate a LinkedIn post from a video summary

**Request Body**:
```json
{
  "summary": "Video summary text...",
  "video_title": "Video Title",
  "video_url": "https://www.youtube.com/watch?v=VIDEO_ID",
  "speaker_name": "Speaker Name",
  "hashtags": ["ai", "machinelearning"],
  "tone": "professional",
  "voice": "first_person",
  "audience": "technical",
  "include_call_to_action": true,
  "max_length": 1200,
  "openai_api_key": "your_openai_api_key"  // Optional, provide your own OpenAI API key
}
```

**Response**:
```json
{
  "post_content": "Generated LinkedIn post content...",
  "character_count": 800,
  "estimated_read_time": "About 1 minute",
  "hashtags_used": ["#ai", "#machinelearning"]
}
```

### 4. Output Formatting

**Endpoint**: `/api/v1/output`  
**Method**: POST  
**Description**: Format the LinkedIn post for output

**Request Body**:
```json
{
  "post_content": "LinkedIn post content...",
  "format": "json"
}
```

**Response**:
```json
{
  "content": {
    "post_content": "LinkedIn post content...",
    "character_count": 800
  },
  "format": "json"
}
```

## Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| OPENAI_API_KEY | OpenAI API key for summarization and post generation | No (can be provided in requests) |
| YOUTUBE_API_KEY | YouTube Data API key for fetching video metadata | No (can be provided in requests) |
| PORT | Port to run the server on (default: 8000) | No |

> **Note**: While environment variables for API keys are optional (as they can be provided in each request), it's recommended to set them for local development and testing. When deploying to Smithery, users will need to provide their own API keys in the requests.

## License

MIT
