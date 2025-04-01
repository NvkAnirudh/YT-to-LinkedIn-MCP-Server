from fastapi import APIRouter, HTTPException, Depends
from app.models.models import OutputRequest, OutputResponse
from app.services.output_service import OutputService
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

def get_output_service():
    return OutputService()

@router.post("/output", response_model=OutputResponse, tags=["Output"])
async def format_output(
    request: OutputRequest,
    output_service: OutputService = Depends(get_output_service)
):
    """
    Format the LinkedIn post for output.
    
    - **post_content**: LinkedIn post content
    - **format**: Output format (json or text)
    
    Returns the formatted LinkedIn post.
    """
    try:
        logger.info(f"Formatting output in {request.format} format")
        result = await output_service.format_output(
            post_content=request.post_content,
            format=request.format
        )
        
        if "error" in result and result["error"]:
            logger.error(f"Error formatting output: {result['error']}")
            raise HTTPException(status_code=400, detail=result["error"])
        
        return OutputResponse(
            content=result.get("content", ""),
            format=result.get("format", request.format)
        )
    except Exception as e:
        logger.exception(f"Unexpected error in format_output: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
