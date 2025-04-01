import logging
import json
from typing import Dict, Any, Union
from app.models.models import OutputFormat

logger = logging.getLogger(__name__)

class OutputService:
    def __init__(self):
        pass
    
    async def format_output(
        self,
        post_content: str,
        format: OutputFormat = OutputFormat.JSON
    ) -> Dict[str, Any]:
        """Format the LinkedIn post for output."""
        try:
            if format == OutputFormat.JSON:
                # Format as JSON
                output = {
                    "post_content": post_content,
                    "character_count": len(post_content)
                }
                return {
                    "content": output,
                    "format": format
                }
            else:
                # Format as plain text
                return {
                    "content": post_content,
                    "format": format
                }
        except Exception as e:
            error_msg = f"Error formatting output: {str(e)}"
            logger.error(error_msg)
            return {"error": error_msg, "content": "", "format": format}
