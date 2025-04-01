from pydantic import BaseModel, Field, HttpUrl
from typing import List, Optional, Dict, Any, Union
from enum import Enum


class ToneEnum(str, Enum):
    EDUCATIONAL = "educational"
    INSPIRATIONAL = "inspirational"
    PROFESSIONAL = "professional"
    CONVERSATIONAL = "conversational"
    THOUGHT_LEADER = "thought_leader"


class AudienceEnum(str, Enum):
    GENERAL = "general"
    TECHNICAL = "technical"
    EXECUTIVE = "executive"
    ENTRY_LEVEL = "entry_level"
    INDUSTRY_SPECIFIC = "industry_specific"


class VoiceEnum(str, Enum):
    FIRST_PERSON = "first_person"
    THIRD_PERSON = "third_person"


class TranscriptRequest(BaseModel):
    youtube_url: HttpUrl = Field(..., description="YouTube video URL")
    language: Optional[str] = Field("en", description="Language code for transcript")
    youtube_api_key: Optional[str] = Field(None, description="YouTube Data API key")


class TranscriptResponse(BaseModel):
    video_id: str = Field(..., description="YouTube video ID")
    video_title: str = Field(..., description="YouTube video title")
    transcript: str = Field(..., description="Extracted transcript text")
    language: str = Field(..., description="Language of the transcript")
    duration_seconds: int = Field(..., description="Video duration in seconds")
    channel_name: Optional[str] = Field(None, description="YouTube channel name")
    error: Optional[str] = Field(None, description="Error message if any")


class SummaryRequest(BaseModel):
    transcript: str = Field(..., description="Video transcript text")
    video_title: str = Field(..., description="Video title")
    tone: ToneEnum = Field(ToneEnum.PROFESSIONAL, description="Tone of the summary")
    audience: AudienceEnum = Field(AudienceEnum.GENERAL, description="Target audience")
    max_length: Optional[int] = Field(250, description="Maximum summary length in words")
    min_length: Optional[int] = Field(150, description="Minimum summary length in words")
    openai_api_key: Optional[str] = Field(None, description="OpenAI API key")


class SummaryResponse(BaseModel):
    summary: str = Field(..., description="Generated summary")
    word_count: int = Field(..., description="Word count of the summary")
    key_points: List[str] = Field(..., description="Key points extracted from the video")


class PostGenerationRequest(BaseModel):
    summary: str = Field(..., description="Video summary")
    video_title: str = Field(..., description="Video title")
    video_url: HttpUrl = Field(..., description="YouTube video URL")
    speaker_name: Optional[str] = Field(None, description="Name of the speaker in the video")
    hashtags: Optional[List[str]] = Field(None, description="List of hashtags to include")
    tone: ToneEnum = Field(ToneEnum.PROFESSIONAL, description="Tone of the post")
    voice: VoiceEnum = Field(VoiceEnum.FIRST_PERSON, description="Voice of the post")
    audience: AudienceEnum = Field(AudienceEnum.GENERAL, description="Target audience")
    include_call_to_action: bool = Field(True, description="Include a call to action")
    max_length: Optional[int] = Field(1200, description="Maximum post length in characters")
    openai_api_key: Optional[str] = Field(None, description="OpenAI API key")


class PostGenerationResponse(BaseModel):
    post_content: str = Field(..., description="Generated LinkedIn post content")
    character_count: int = Field(..., description="Character count of the post")
    estimated_read_time: str = Field(..., description="Estimated read time")
    hashtags_used: List[str] = Field(..., description="Hashtags used in the post")


class OutputFormat(str, Enum):
    JSON = "json"
    TEXT = "text"


class OutputRequest(BaseModel):
    post_content: str = Field(..., description="LinkedIn post content")
    format: OutputFormat = Field(OutputFormat.JSON, description="Output format")


class OutputResponse(BaseModel):
    content: Union[str, Dict[str, Any]] = Field(..., description="Formatted output content")
    format: OutputFormat = Field(..., description="Output format")
