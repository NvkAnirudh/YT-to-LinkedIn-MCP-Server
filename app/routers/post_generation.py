from fastapi import APIRouter, HTTPException, Depends
from app.models.models import PostGenerationRequest, PostGenerationResponse
from app.services.post_generation_service import PostGenerationService
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

def get_post_generation_service():
    return PostGenerationService()

@router.post("/generate-post", response_model=PostGenerationResponse, tags=["Post Generation"])
async def generate_post(
    request: PostGenerationRequest,
    post_service: PostGenerationService = Depends(get_post_generation_service)
):
    """
    Generate a LinkedIn post from a video summary.
    
    - **summary**: Video summary
    - **video_title**: Title of the video
    - **video_url**: URL of the YouTube video
    - **speaker_name**: Name of the speaker in the video (optional)
    - **hashtags**: List of hashtags to include (optional)
    - **tone**: Tone of the post (educational, inspirational, professional, conversational, thought_leader)
    - **voice**: Voice of the post (first_person, third_person)
    - **audience**: Target audience (general, technical, executive, entry_level, industry_specific)
    - **include_call_to_action**: Whether to include a call to action
    - **max_length**: Maximum post length in characters
    - **openai_api_key**: Optional OpenAI API key
    
    Returns a LinkedIn post draft.
    """
    try:
        logger.info(f"Generating LinkedIn post for video: {request.video_title}")
        result = await post_service.generate_post(
            summary=request.summary,
            video_title=request.video_title,
            video_url=str(request.video_url),
            speaker_name=request.speaker_name,
            hashtags=request.hashtags,
            tone=request.tone,
            voice=request.voice,
            audience=request.audience,
            include_call_to_action=request.include_call_to_action,
            max_length=request.max_length,
            api_key=request.openai_api_key
        )
        
        if "error" in result and result["error"]:
            logger.error(f"Error generating LinkedIn post: {result['error']}")
            raise HTTPException(status_code=400, detail=result["error"])
        
        return PostGenerationResponse(
            post_content=result.get("post_content", ""),
            character_count=result.get("character_count", 0),
            estimated_read_time=result.get("estimated_read_time", ""),
            hashtags_used=result.get("hashtags_used", [])
        )
    except Exception as e:
        logger.exception(f"Unexpected error in generate_post: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
