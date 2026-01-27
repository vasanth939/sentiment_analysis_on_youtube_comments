from googleapiclient.discovery import build
import pandas as pd
import logging

import os
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("YOUTUBE_API_KEY")

logger = logging.getLogger(__name__)

def get_video_id(url):
    if "v=" in url:
        return url.split("v=")[1].split("&")[0]
    elif "youtu.be/" in url:
        return url.split("youtu.be/")[1].split("?")[0]
    else:
        return url

def get_youtube_service():
    return build("youtube", "v3", developerKey=API_KEY)

def fetch_video_details(video_url):
    video_id = get_video_id(video_url)
    youtube = get_youtube_service()
    
    request = youtube.videos().list(
        part="snippet,statistics",
        id=video_id
    )
    response = request.execute()
    
    if not response["items"]:
        return None
        
    item = response["items"][0]
    snippet = item["snippet"]
    stats = item["statistics"]
    
    return {
        "title": snippet["title"],
        "channelTitle": snippet["channelTitle"],
        "publishedAt": snippet["publishedAt"][:10], # YYYY-MM-DD
        "viewCount": stats.get("viewCount", 0),
        "likeCount": stats.get("likeCount", 0),
        "commentCount": stats.get("commentCount", 0),
        "thumbnail": snippet["thumbnails"]["high"]["url"]
    }

def fetch_comments(video_url):
    video_id = get_video_id(video_url)
    youtube = get_youtube_service()

    comments = []

    request = youtube.commentThreads().list(
        part="snippet",
        videoId=video_id,
        maxResults=50,
        textFormat="plainText"
    )

    response = request.execute()

    for item in response["items"]:
        comment = item["snippet"]["topLevelComment"]["snippet"]["textDisplay"]
        author = item["snippet"]["topLevelComment"]["snippet"]["authorDisplayName"]
        published_at = item["snippet"]["topLevelComment"]["snippet"]["publishedAt"]
        comments.append([author, comment, published_at])

    df = pd.DataFrame(comments, columns=["author", "comment", "date"])
    df.to_csv("data/comments.csv", index=False)
    
    logger.info("[SUCCESS] Comments fetched and saved to data/comments.csv")
