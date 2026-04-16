from googleapiclient.discovery import build
import pandas as pd
import logging
import time
from datetime import datetime, timezone
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
    elif "/live/" in url:
        return url.split("/live/")[1].split("?")[0].strip("/")
    elif "/shorts/" in url:
        return url.split("/shorts/")[1].split("?")[0].strip("/")
    else:
        return url

def get_youtube_service():
    return build("youtube", "v3", developerKey=API_KEY)

def fetch_video_details(video_url):
    video_id = get_video_id(video_url)
    youtube = get_youtube_service()
    
    request = youtube.videos().list(
        part="snippet,statistics,liveStreamingDetails",
        id=video_id
    )
    response = request.execute()
    
    if not response["items"]:
        return None
        
    item = response["items"][0]
    snippet = item["snippet"]
    stats = item["statistics"]
    live_details = item.get("liveStreamingDetails", {})
    
    return {
        "title": snippet["title"],
        "channelTitle": snippet["channelTitle"],
        "publishedAt": snippet["publishedAt"][:10], # YYYY-MM-DD
        "viewCount": stats.get("viewCount", 0),
        "likeCount": stats.get("likeCount", 0),
        "commentCount": stats.get("commentCount", 0),
        "thumbnail": snippet["thumbnails"]["high"]["url"],
        "isLive": "activeLiveChatId" in live_details,
        "concurrentViewers": live_details.get("concurrentViewers", "N/A")
    }

def fetch_comments(video_url):
    start_time = time.time()
    video_id = get_video_id(video_url)
    youtube = get_youtube_service()

    # Get expected comment count to prevent over-fetching and speed up termination
    video_details = fetch_video_details(video_url)
    expected_comment_count = float('inf')
    if video_details and video_details.get("commentCount"):
        try:
            expected_comment_count = int(video_details["commentCount"])
        except ValueError:
            pass

    comments = []

    
    # Check if video is live/replay to decide strategy
    is_live_or_replay = False
    active_live_chat_id = None
    
    try:
        vid_req = youtube.videos().list(
             part="liveStreamingDetails",
             id=video_id
        )
        vid_resp = vid_req.execute()
        if vid_resp["items"]:
             live_details = vid_resp["items"][0].get("liveStreamingDetails")
             if live_details:
                 is_live_or_replay = True
                 if "activeLiveChatId" in live_details:
                     active_live_chat_id = live_details["activeLiveChatId"]
    except Exception as e:
        logger.warning(f"Failed to check live status: {e}")

    # --- 1. Attempt to fetch Live Chat (History + Current) ---
    # We prioritize ChatDownloader because it fetches history better than the API for active streams, and handles replays.
    fetched_live_chat = False
    
    if is_live_or_replay:
        try:
             logger.info("Live/Replay detected. Attempting to fetch Chat via chat-downloader...")
             from chat_downloader import ChatDownloader
             
             # Create a downloader instance
             downloader = ChatDownloader()
             chat = downloader.get_chat(video_url)
             
             count = 0
             max_chat_messages = 50000 # Increased limit for huge videos
             
             # Current time in UTC for breaking live loop
             now_utc = datetime.now(timezone.utc)
             
             for message in chat:
                 auth_name = message.get("author", {}).get("name", "Anonymous")
                 msg = message.get("message", "")
                 
                 timestamp = message.get("timestamp") # microseconds
                 if timestamp:
                     ts_dt = pd.Timestamp.fromtimestamp(timestamp / 1000000, tz=timezone.utc)
                     pub_at = str(ts_dt)
                     
                     # If currently live, break if we are close to 'now' (within 10 seconds)
                     # to avoid infinite stream listening during report generation
                     if active_live_chat_id:
                         time_diff = (now_utc - ts_dt).total_seconds()
                         if time_diff < 10: 
                             # We caught up to live
                             # Continue a bit to ensure we didn't miss rapid bursts, but essentially we are done for a snapshot
                             # Actually 'break' might be too aggressive if latency is high, but prevents hanging.
                             # Let's rely on max_chat_messages or a generic timeout logic if needed.
                             # For now, let's just use the max count or explicit break if we clearly passed 'now' (unlikely with timestamps)
                             pass
                 else:
                     pub_at = str(pd.Timestamp.now())
                 
                 comments.append([auth_name, msg, pub_at])
                 count += 1
                 
                 if count >= max_chat_messages:
                     logger.info("Reached max chat messages limit.")
                     break
            
             logger.info(f"Fetched {count} live chat messages via chat-downloader.")
             fetched_live_chat = True
             
        except Exception as e:
             logger.warning(f"Chat-downloader failed or not installed/compatible: {e}")
             fetched_live_chat = False

    # --- 2. Fallback: Live Chat API (if ChatDownloader failed AND it is active live) ---
    if not fetched_live_chat and active_live_chat_id:
        try:
             logger.info(f"Fallback: Fetching active live chat ({active_live_chat_id}) via API...")
             
             next_page_token = None
             api_chat_count = 0
             max_api_chat = 50000 # Fetch more pages via API
             
             while api_chat_count < max_api_chat:
                 if time.time() - start_time > 300:
                     logger.info("Timeout safety triggered in live API chat.")
                     break
                 
                 lc_req = youtube.liveChatMessages().list(
                     liveChatId=active_live_chat_id,
                     part="snippet,authorDetails",
                     maxResults=50,
                     pageToken=next_page_token
                 )
                 lc_resp = lc_req.execute()
                 
                 items = lc_resp.get("items", [])
                 if not items:
                     break
                     
                 for item in items:
                     snippet = item["snippet"]
                     msg = snippet.get("displayMessage", "")
                     author_info = item.get("authorDetails", {})
                     auth_name = author_info.get("displayName", "Anonymous")
                     pub_at = snippet.get("publishedAt", "")
                     if not pub_at:
                         pub_at = str(pd.Timestamp.now(tz='UTC'))

                     comments.append([auth_name, msg, pub_at])
                     api_chat_count += 1
                 
                 next_page_token = lc_resp.get("nextPageToken")
                 # The API tells us how long to wait, but for a snapshot fetch we might just want what's available NOW.
                 # Real-time polling requires sleeping pollingIntervalMillis.
                 # Since we want a snapshot, we might not want to sleep and wait for new ones.
                 # If nextPageToken is provided, it usually means 'wait this long then ask again'.
                 # So efficiently, one call gives us the buffer. We might stop here.
                 if not next_page_token:
                     break
                 
             logger.info(f"Fetched {api_chat_count} live chat messages via API.")
             
        except Exception as e:
            logger.warning(f"Live chat API fetch failed: {e}")

    # --- 3. Fetch Standard Comments (Always try, for mixed content or VODs) ---
    # Even live videos might have standard comments if they are long running or replays? 
    # Usually Live has Chat, VOD has Comments. But sometimes both.
    
    logger.info(f"Starting standard comment fetch for video {video_id}...")

    next_page_token = None
    
    while True:
        try:
            response = youtube.commentThreads().list(
                part="snippet,replies",
                videoId=video_id,
                maxResults=100,
                textFormat="plainText",
                pageToken=next_page_token
            ).execute()
        except Exception as e:
            logger.warning(f"Could not fetch standard comments (might be disabled): {e}")
            break
            
        for item in response.get("items", []):
            # Top-level comment
            top_snp = item["snippet"]["topLevelComment"]["snippet"]
            
            comments.append([
                top_snp.get("authorDisplayName", "Unknown"),
                top_snp.get("textDisplay", ""),
                top_snp.get("publishedAt", "")
            ])
            
            # Handle replies seamlessly from the same API response
            if "replies" in item:
                for reply in item["replies"].get("comments", []):
                    rs = reply["snippet"]
                    comments.append([
                        rs.get("authorDisplayName", "Unknown"),
                        rs.get("textDisplay", ""),
                        rs.get("publishedAt", "")
                    ])
                        
        next_page_token = response.get("nextPageToken")
        if not next_page_token:
            break

    df = pd.DataFrame(comments, columns=["author", "comment", "date"])
    
    # Drop duplicates in case of API pagination overlap
    df.drop_duplicates(subset=["author", "comment", "date"], inplace=True)
    
    # Ensure data directory exists
    if not os.path.exists("data"):
        os.makedirs("data")
        
    df.to_csv("data/comments.csv", index=False, encoding='utf-8') 
    
    logger.info(f"[SUCCESS] {len(df)} total comments/chat-messages fetched and saved.")
