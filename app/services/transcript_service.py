import re
import logging
from typing import Dict, Any, Optional, Tuple
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import os
from urllib.parse import urlparse, parse_qs

logger = logging.getLogger(__name__)

class TranscriptService:
    def __init__(self):
        self.youtube_api_key = os.getenv("YOUTUBE_API_KEY")
        if not self.youtube_api_key:
            logger.warning("YOUTUBE_API_KEY not found in environment variables")
    
    def extract_video_id(self, youtube_url: str) -> str:
        """Extract the video ID from a YouTube URL."""
        # Handle different URL formats
        parsed_url = urlparse(youtube_url)
        
        if parsed_url.netloc == 'youtu.be':
            return parsed_url.path[1:]
        
        if parsed_url.netloc in ('www.youtube.com', 'youtube.com'):
            if parsed_url.path == '/watch':
                return parse_qs(parsed_url.query)['v'][0]
            elif parsed_url.path.startswith('/embed/'):
                return parsed_url.path.split('/')[2]
            elif parsed_url.path.startswith('/v/'):
                return parsed_url.path.split('/')[2]
        
        # If we get here, we couldn't extract a video ID
        raise ValueError(f"Could not extract video ID from URL: {youtube_url}")
    
    def get_video_metadata(self, video_id: str, api_key: Optional[str] = None) -> Dict[str, Any]:
        """Get video metadata using YouTube Data API."""
        # Use the provided API key if available, otherwise fall back to the environment variable
        youtube_api_key = api_key or self.youtube_api_key
        
        if not youtube_api_key:
            logger.warning("YouTube API key not available. Limited metadata will be returned.")
            return {"video_id": video_id}
        
        try:
            youtube = build('youtube', 'v3', developerKey=youtube_api_key)
            response = youtube.videos().list(
                part='snippet,contentDetails',
                id=video_id
            ).execute()
            
            if not response['items']:
                logger.error(f"No video found with ID: {video_id}")
                return {"video_id": video_id, "error": "Video not found"}
            
            video_info = response['items'][0]
            snippet = video_info['snippet']
            
            # Parse duration
            duration_str = video_info['contentDetails']['duration']
            duration_seconds = self._parse_duration(duration_str)
            
            return {
                "video_id": video_id,
                "video_title": snippet['title'],
                "channel_name": snippet['channelTitle'],
                "duration_seconds": duration_seconds,
                "published_at": snippet['publishedAt']
            }
        except HttpError as e:
            logger.error(f"YouTube API error: {str(e)}")
            return {"video_id": video_id, "error": f"YouTube API error: {str(e)}"}
        except Exception as e:
            logger.error(f"Error fetching video metadata: {str(e)}")
            return {"video_id": video_id, "error": f"Error fetching video metadata: {str(e)}"}
    
    def _parse_duration(self, duration_str: str) -> int:
        """Parse ISO 8601 duration format to seconds."""
        # Remove 'PT' prefix
        duration = duration_str[2:]
        hours, minutes, seconds = 0, 0, 0
        
        # Extract hours, minutes, seconds
        if 'H' in duration:
            hours_part = duration.split('H')[0]
            hours = int(hours_part)
            duration = duration.split('H')[1]
        
        if 'M' in duration:
            minutes_part = duration.split('M')[0]
            minutes = int(minutes_part)
            duration = duration.split('M')[1]
        
        if 'S' in duration:
            seconds_part = duration.split('S')[0]
            seconds = int(seconds_part)
        
        return hours * 3600 + minutes * 60 + seconds
    
    def get_transcript(self, video_id: str, language: str = 'en') -> Tuple[str, str]:
        """Get transcript for a YouTube video."""
        try:
            transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
            
            # Try to get the transcript in the requested language
            try:
                transcript = transcript_list.find_transcript([language])
            except NoTranscriptFound:
                # If not found, try to get any transcript and translate it
                logger.info(f"No transcript found in {language}, trying to find any available transcript")
                transcript = transcript_list.find_transcript([])
                transcript = transcript.translate(language)
            
            transcript_data = transcript.fetch()
            
            # Combine all transcript parts into a single text
            full_transcript = " ".join([part['text'] for part in transcript_data])
            
            # Clean up the transcript
            cleaned_transcript = self._clean_transcript(full_transcript)
            
            return cleaned_transcript, transcript.language_code
            
        except TranscriptsDisabled:
            logger.error(f"Transcripts are disabled for video: {video_id}")
            raise ValueError("Transcripts are disabled for this video")
        except NoTranscriptFound:
            logger.error(f"No transcript found for video: {video_id}")
            raise ValueError("No transcript found for this video")
        except Exception as e:
            logger.error(f"Error fetching transcript: {str(e)}")
            raise ValueError(f"Error fetching transcript: {str(e)}")
    
    def _clean_transcript(self, transcript: str) -> str:
        """Clean up the transcript text."""
        # Remove timestamps if present
        transcript = re.sub(r'\[\d+:\d+\]', '', transcript)
        
        # Remove speaker labels if present (e.g., "Speaker 1:", "John:")
        transcript = re.sub(r'^\s*\w+\s*:', '', transcript, flags=re.MULTILINE)
        
        # Remove multiple spaces
        transcript = re.sub(r'\s+', ' ', transcript)
        
        # Remove special characters
        transcript = re.sub(r'[^\w\s.,?!-]', '', transcript)
        
        return transcript.strip()
    
    async def extract_transcript(self, youtube_url: str, language: str = 'en', api_key: Optional[str] = None) -> Dict[str, Any]:
        """Extract transcript and metadata from a YouTube video."""
        try:
            video_id = self.extract_video_id(youtube_url)
            metadata = self.get_video_metadata(video_id, api_key)
            
            if "error" in metadata and metadata["error"]:
                return {**metadata, "transcript": ""}
            
            transcript_text, detected_language = self.get_transcript(video_id, language)
            
            return {
                **metadata,
                "transcript": transcript_text,
                "language": detected_language
            }
        except ValueError as e:
            logger.error(f"Value error: {str(e)}")
            return {
                "video_id": "",
                "error": str(e),
                "transcript": ""
            }
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            return {
                "video_id": "",
                "error": f"Unexpected error: {str(e)}",
                "transcript": ""
            }
