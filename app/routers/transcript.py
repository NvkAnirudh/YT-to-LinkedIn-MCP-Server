from fastapi import APIRouter, HTTPException, Depends
from app.models.models import TranscriptRequest, TranscriptResponse
from app.services.transcript_service import TranscriptService
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

def get_transcript_service():
    return TranscriptService()

@router.post("/transcript", response_model=TranscriptResponse, tags=["Transcript"])
async def extract_transcript(
    request: TranscriptRequest,
    transcript_service: TranscriptService = Depends(get_transcript_service)
):
    """
    Extract transcript from a YouTube video.
    
    - **youtube_url**: URL of the YouTube video
    - **language**: Language code for the transcript (default: en)
    - **youtube_api_key**: Optional YouTube Data API key
    
    Returns the video transcript and metadata.
    """
    try:
        logger.info(f"Extracting transcript for URL: {request.youtube_url}")
        result = await transcript_service.extract_transcript(
            youtube_url=str(request.youtube_url),
            language=request.language,
            api_key=request.youtube_api_key
        )
        
        if "error" in result and result["error"]:
            logger.error(f"Error extracting transcript: {result['error']}")
            raise HTTPException(status_code=400, detail=result["error"])
        
        return TranscriptResponse(
            video_id=result.get("video_id", ""),
            video_title=result.get("video_title", "Unknown Title"),
            transcript=result.get("transcript", ""),
            language=result.get("language", request.language),
            duration_seconds=result.get("duration_seconds", 0),
            channel_name=result.get("channel_name", None),
            error=result.get("error", None)
        )
    except Exception as e:
        logger.exception(f"Unexpected error in extract_transcript: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
