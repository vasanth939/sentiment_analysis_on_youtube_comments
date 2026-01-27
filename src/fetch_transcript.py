from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import TextFormatter

def get_video_id(url):
    if "v=" in url:
        return url.split("v=")[1].split("&")[0]
    elif "youtu.be/" in url:
        return url.split("youtu.be/")[1].split("?")[0]
    else:
        return url

def fetch_transcript_text(video_url):
    """
    Fetches the transcript for a given YouTube video URL.
    Returns the transcript as a single string or None if not available.
    """
    video_id = get_video_id(video_url)
    try:
        # get_transcript returns a list of dictionaries
        transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
        
        # Formatter to convert to plain text
        formatter = TextFormatter()
        text_formatted = formatter.format_transcript(transcript_list)
        
        return text_formatted
    except Exception as e:
        print(f"Could not fetch transcript: {e}")
        return None
