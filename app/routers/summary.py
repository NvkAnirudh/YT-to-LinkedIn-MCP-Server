from fastapi import APIRouter, HTTPException, Depends
from app.models.models import SummaryRequest, SummaryResponse
from app.services.summary_service import SummaryService
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

def get_summary_service():
    return SummaryService()

@router.post("/summarize", response_model=SummaryResponse, tags=["Summary"])
async def generate_summary(
    request: SummaryRequest,
    summary_service: SummaryService = Depends(get_summary_service)
):
    """
    Generate a summary from a video transcript.
    
    - **transcript**: Video transcript text
    - **video_title**: Title of the video
    - **tone**: Tone of the summary (educational, inspirational, professional, conversational, thought_leader)
    - **audience**: Target audience (general, technical, executive, entry_level, industry_specific)
    - **max_length**: Maximum summary length in words
    - **min_length**: Minimum summary length in words
    - **openai_api_key**: Optional OpenAI API key
    
    Returns a summary of the video content.
    """
    try:
        logger.info(f"Generating summary for video: {request.video_title}")
        result = await summary_service.generate_summary(
            transcript=request.transcript,
            video_title=request.video_title,
            tone=request.tone,
            audience=request.audience,
            min_length=request.min_length,
            max_length=request.max_length,
            api_key=request.openai_api_key
        )
        
        if "error" in result and result["error"]:
            logger.error(f"Error generating summary: {result['error']}")
            raise HTTPException(status_code=400, detail=result["error"])
        
        return SummaryResponse(
            summary=result.get("summary", ""),
            word_count=result.get("word_count", 0),
            key_points=result.get("key_points", [])
        )
    except Exception as e:
        logger.exception(f"Unexpected error in generate_summary: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
