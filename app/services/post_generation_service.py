import logging
import os
from typing import Dict, Any, List, Optional
import openai
import re
from app.models.models import ToneEnum, AudienceEnum, VoiceEnum

logger = logging.getLogger(__name__)

class PostGenerationService:
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            logger.warning("OPENAI_API_KEY not found in environment variables")
        else:
            openai.api_key = self.api_key
    
    async def generate_post(
        self,
        summary: str,
        video_title: str,
        video_url: str,
        speaker_name: Optional[str] = None,
        hashtags: Optional[List[str]] = None,
        tone: ToneEnum = ToneEnum.PROFESSIONAL,
        voice: VoiceEnum = VoiceEnum.FIRST_PERSON,
        audience: AudienceEnum = AudienceEnum.GENERAL,
        include_call_to_action: bool = True,
        max_length: int = 1200,
        api_key: Optional[str] = None
    ) -> Dict[str, Any]:
        """Generate a LinkedIn post based on the video summary."""
        # Use the provided API key if available, otherwise fall back to the environment variable
        openai_api_key = api_key or self.api_key
        
        if not openai_api_key:
            error_msg = "OpenAI API key not configured"
            logger.error(error_msg)
            return {"error": error_msg, "post_content": ""}
        
        if not summary:
            error_msg = "Empty summary provided"
            logger.error(error_msg)
            return {"error": error_msg, "post_content": ""}
        
        try:
            # Prepare the prompt for the language model
            prompt = self._create_post_prompt(
                summary=summary,
                video_title=video_title,
                video_url=video_url,
                speaker_name=speaker_name,
                hashtags=hashtags,
                tone=tone,
                voice=voice,
                audience=audience,
                include_call_to_action=include_call_to_action,
                max_length=max_length
            )
            
            # Call the OpenAI API
            client = openai.OpenAI(api_key=openai_api_key)
            response = client.chat.completions.create(
                model="gpt-4",  # Use appropriate model based on needs
                messages=[
                    {"role": "system", "content": "You are a professional content creator specializing in LinkedIn posts that drive engagement."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=1000,
                top_p=1.0,
                frequency_penalty=0.0,
                presence_penalty=0.0
            )
            
            # Process the response
            post_content = response.choices[0].message.content.strip()
            
            # Extract hashtags used in the post
            hashtags_used = self._extract_hashtags(post_content)
            
            # Calculate character count
            character_count = len(post_content)
            
            # Calculate estimated read time (average reading speed: 265 characters per minute)
            read_time_minutes = character_count / 1325  # 265 chars/min * 5 = 1325 chars/5min
            if read_time_minutes < 1:
                estimated_read_time = "Less than a minute"
            else:
                estimated_read_time = f"About {int(read_time_minutes)} minute{'s' if int(read_time_minutes) > 1 else ''}"
            
            return {
                "post_content": post_content,
                "character_count": character_count,
                "estimated_read_time": estimated_read_time,
                "hashtags_used": hashtags_used
            }
            
        except Exception as e:
            error_msg = f"Error generating LinkedIn post: {str(e)}"
            logger.error(error_msg)
            return {"error": error_msg, "post_content": ""}
    
    def _create_post_prompt(
        self,
        summary: str,
        video_title: str,
        video_url: str,
        speaker_name: Optional[str],
        hashtags: Optional[List[str]],
        tone: ToneEnum,
        voice: VoiceEnum,
        audience: AudienceEnum,
        include_call_to_action: bool,
        max_length: int
    ) -> str:
        """Create a prompt for the language model."""
        audience_descriptions = {
            AudienceEnum.GENERAL: "general professionals on LinkedIn",
            AudienceEnum.TECHNICAL: "technical professionals and specialists",
            AudienceEnum.EXECUTIVE: "executives and decision-makers",
            AudienceEnum.ENTRY_LEVEL: "professionals new to the field",
            AudienceEnum.INDUSTRY_SPECIFIC: "industry-specific professionals"
        }
        
        tone_descriptions = {
            ToneEnum.EDUCATIONAL: "educational and informative",
            ToneEnum.INSPIRATIONAL: "inspirational and motivational",
            ToneEnum.PROFESSIONAL: "professional and authoritative",
            ToneEnum.CONVERSATIONAL: "conversational and approachable",
            ToneEnum.THOUGHT_LEADER: "thought-provoking and visionary"
        }
        
        voice_descriptions = {
            VoiceEnum.FIRST_PERSON: "first-person (using I, we, my, our)",
            VoiceEnum.THIRD_PERSON: "third-person (objective, reporting style)"
        }
        
        hashtag_str = ""
        if hashtags and len(hashtags) > 0:
            hashtag_str = "Include these hashtags in your post (preferably at the end): " + ", ".join([f"#{tag.strip('#')}" for tag in hashtags])
        
        speaker_str = ""
        if speaker_name:
            speaker_str = f"The speaker/creator of the video is: {speaker_name}"
        
        cta_str = ""
        if include_call_to_action:
            cta_str = "Include a soft call to action at the end (e.g., asking for thoughts, suggesting to watch the video, etc.)"
        
        prompt = f"""
        Create an engaging LinkedIn post based on a YouTube video summary.
        
        Video Title: {video_title}
        Video URL: {video_url}
        {speaker_str}
        
        Post requirements:
        - Maximum length: {max_length} characters (LinkedIn optimal length)
        - Tone: {tone_descriptions.get(tone, "professional")}
        - Voice: {voice_descriptions.get(voice, "first-person")}
        - Target Audience: {audience_descriptions.get(audience, "general professionals")}
        - Structure: Start with an engaging hook, share insights from the video, and end with a thought-provoking question or call to action
        - Format: Use line breaks and emojis appropriately to make the post visually appealing and easy to read
        - Include the video URL somewhere in the post
        {hashtag_str}
        {cta_str}
        
        Here is the summary of the video:
        {summary}
        
        Create a LinkedIn post that feels authentic, valuable, and encourages engagement.
        """
        
        return prompt
    
    def _extract_hashtags(self, post_content: str) -> List[str]:
        """Extract hashtags from the post content."""
        # Find all hashtags in the post
        hashtags = re.findall(r'#(\w+)', post_content)
        return [f"#{tag}" for tag in hashtags]
