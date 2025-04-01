import logging
import os
from typing import Dict, Any, List, Optional
import openai
from app.models.models import ToneEnum, AudienceEnum

logger = logging.getLogger(__name__)

class SummaryService:
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            logger.warning("OPENAI_API_KEY not found in environment variables")
        else:
            openai.api_key = self.api_key
    
    async def generate_summary(
        self, 
        transcript: str, 
        video_title: str,
        tone: ToneEnum = ToneEnum.PROFESSIONAL,
        audience: AudienceEnum = AudienceEnum.GENERAL,
        min_length: int = 150,
        max_length: int = 250,
        api_key: Optional[str] = None
    ) -> Dict[str, Any]:
        """Generate a summary of the transcript using OpenAI GPT."""
        # Use the provided API key if available, otherwise fall back to the environment variable
        openai_api_key = api_key or self.api_key
        
        if not openai_api_key:
            error_msg = "OpenAI API key not configured"
            logger.error(error_msg)
            return {"error": error_msg, "summary": "", "key_points": []}
        
        if not transcript:
            error_msg = "Empty transcript provided"
            logger.error(error_msg)
            return {"error": error_msg, "summary": "", "key_points": []}
        
        try:
            # Prepare the prompt for the language model
            prompt = self._create_summary_prompt(
                transcript=transcript,
                video_title=video_title,
                tone=tone,
                audience=audience,
                min_length=min_length,
                max_length=max_length
            )
            
            # Call the OpenAI API
            client = openai.OpenAI(api_key=openai_api_key)
            response = client.chat.completions.create(
                model="gpt-4",  # Use appropriate model based on needs
                messages=[
                    {"role": "system", "content": "You are a professional content summarizer that creates concise, insightful summaries of video transcripts."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.5,
                max_tokens=1000,
                top_p=1.0,
                frequency_penalty=0.0,
                presence_penalty=0.0
            )
            
            # Process the response
            response_text = response.choices[0].message.content.strip()
            
            # Parse the response to extract summary and key points
            summary, key_points = self._parse_response(response_text)
            
            # Count words in summary
            word_count = len(summary.split())
            
            return {
                "summary": summary,
                "key_points": key_points,
                "word_count": word_count
            }
            
        except Exception as e:
            error_msg = f"Error generating summary: {str(e)}"
            logger.error(error_msg)
            return {"error": error_msg, "summary": "", "key_points": []}
    
    def _create_summary_prompt(
        self,
        transcript: str,
        video_title: str,
        tone: ToneEnum,
        audience: AudienceEnum,
        min_length: int,
        max_length: int
    ) -> str:
        """Create a prompt for the language model."""
        # Truncate transcript if it's too long
        max_transcript_length = 15000  # Adjust based on token limits
        if len(transcript) > max_transcript_length:
            transcript = transcript[:max_transcript_length] + "..."
        
        audience_descriptions = {
            AudienceEnum.GENERAL: "general audience with varied backgrounds",
            AudienceEnum.TECHNICAL: "technical professionals with domain expertise",
            AudienceEnum.EXECUTIVE: "business executives and decision-makers",
            AudienceEnum.ENTRY_LEVEL: "beginners and those new to the field",
            AudienceEnum.INDUSTRY_SPECIFIC: "industry professionals with specific domain knowledge"
        }
        
        tone_descriptions = {
            ToneEnum.EDUCATIONAL: "educational and informative",
            ToneEnum.INSPIRATIONAL: "inspirational and motivational",
            ToneEnum.PROFESSIONAL: "professional and authoritative",
            ToneEnum.CONVERSATIONAL: "conversational and approachable",
            ToneEnum.THOUGHT_LEADER: "thought-provoking and visionary"
        }
        
        prompt = f"""
        I need you to create a concise summary of a YouTube video based on its transcript.
        
        Video Title: {video_title}
        
        Please create:
        1. A summary between {min_length} and {max_length} words that captures the main points and insights from the video.
        2. A list of 3-5 key points or takeaways from the video.
        
        The summary should be:
        - Tone: {tone_descriptions.get(tone, "professional")}
        - Target Audience: {audience_descriptions.get(audience, "general audience")}
        - Well-structured with clear paragraphs
        - Focused on the most valuable insights
        - Free of redundant information
        
        Format your response as:
        
        SUMMARY:
        [Your summary here]
        
        KEY POINTS:
        - [Key point 1]
        - [Key point 2]
        - [Key point 3]
        - [Key point 4]
        - [Key point 5]
        
        Here is the transcript:
        {transcript}
        """
        
        return prompt
    
    def _parse_response(self, response_text: str) -> tuple[str, List[str]]:
        """Parse the response to extract summary and key points."""
        summary = ""
        key_points = []
        
        # Split the response into sections
        sections = response_text.split("SUMMARY:")
        if len(sections) > 1:
            content = sections[1].strip()
            
            # Split content into summary and key points
            parts = content.split("KEY POINTS:")
            if len(parts) > 1:
                summary = parts[0].strip()
                key_points_text = parts[1].strip()
                
                # Extract key points as a list
                key_points = [point.strip().lstrip("- ") for point in key_points_text.split("\n") if point.strip()]
            else:
                summary = content
        else:
            summary = response_text
        
        return summary, key_points
