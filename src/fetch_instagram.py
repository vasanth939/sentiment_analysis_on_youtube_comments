import instaloader
import pandas as pd
import logging
import os
import re

logger = logging.getLogger(__name__)

def get_shortcode_from_url(url):
    # Extract shortcode from URL like https://www.instagram.com/p/SHORTCODE/
    match = re.search(r'instagram\.com/(?:p|reel)/([^/?#&]+)', url)
    if match:
        return match.group(1)
    return None


def get_instaloader_instance():
    L = instaloader.Instaloader()
    
    # Try to load username from env
    from dotenv import load_dotenv
    load_dotenv()
    
    username = os.getenv("INSTAGRAM_USERNAME")
    password = os.getenv("INSTAGRAM_PASSWORD")
    
    if username:
        try:
            # Try to load session first
            session_file = f"session-{username}"
            if os.path.exists(session_file):
                logger.info(f"Loading Instagram session for {username}...")
                L.load_session_from_file(username, filename=session_file)
            elif password:
                # Login with password if no session (less preferred due to checkpoints)
                logger.info(f"Logging in to Instagram as {username}...")
                L.login(username, password)
            else:
                logger.warning("INSTAGRAM_USERNAME found but no session file or password provided.")
        except Exception as e:
            logger.error(f"Instagram Login Failed: {e}")
            
    return L

def fetch_instagram_details(url):
    L = get_instaloader_instance()
    shortcode = get_shortcode_from_url(url)
    
    if not shortcode:
        logger.error("Could not extract Instagram shortcode/ID from URL")
        return None

    try:
        post = instaloader.Post.from_shortcode(L.context, shortcode)
        
        return {
            "title": post.caption if post.caption else "Instagram Post",
            "channelTitle": post.owner_username,
            "publishedAt": str(post.date_local)[:10],
            "viewCount": post.video_view_count if post.is_video else "N/A",
            "likeCount": post.likes,
            "commentCount": post.comments,
            "thumbnail": post.url, # access to display url
            "isLive": False, 
            "concurrentViewers": "N/A"
        }
    except Exception as e:
        logger.error(f"Error fetching Instagram details: {e}")
        # Return fallback metadata so the app doesn't just 404.
        # This allows the "System Alert" in comments to be displayed to the user.
        return {
            "title": "Instagram Post (Login Required for details)",
            "channelTitle": "Unknown",
            "publishedAt": "N/A",
            "viewCount": "N/A",
            "likeCount": 0,
            "commentCount": 0,
            "thumbnail": "", 
            "isLive": False, 
            "concurrentViewers": "N/A"
        }

def fetch_instagram_comments(url):
    L = get_instaloader_instance()
    shortcode = get_shortcode_from_url(url)
    
    if not shortcode:
        logger.error("Invalid Instagram URL")
        return False
        
    comments_data = []
    
    try:
        # User agent is handled by Instaloader, but custom one can be set if needed
        # L.context.user_agent = ... 
        
        post = instaloader.Post.from_shortcode(L.context, shortcode)
        
        logger.info(f"Fetching comments for Instagram post: {shortcode}")
        
        expected_comments = post.comments
        logger.info(f"Post has {expected_comments} comments according to metadata.")

        count = 0
        max_comments = 100000 # Increased limit to practically "all" for standard use
        
        # Check if we are logged in
        if not L.context.is_logged_in and expected_comments > 0:
             logger.warning("Not logged in. Comments might not be fetched.")
        
        for comment in post.get_comments():
            # Add top-level comment
            comments_data.append([
                comment.owner.username,
                comment.text,
                str(comment.created_at_utc)
            ])
            count += 1
            
            # Add replies (threaded comments)
            for reply in comment.answers:
                comments_data.append([
                    reply.owner.username,
                    reply.text,
                    str(reply.created_at_utc)
                ])
                count += 1
                if count >= max_comments:
                    break
            
            # Check limit after top-level + replies
            if count >= max_comments:
                logger.info(f"Reached safety limit of {max_comments} comments.")
                break
        
        # Fallback: If metadata says there are comments but we got none, check login
        if count == 0 and expected_comments > 0:
            logger.warning("No comments fetched. Login likely required.")
            msg = "Unable to fetch comments. Instagram requires login. Please run 'python setup_instagram.py' to login."
            if not L.context.is_logged_in:
                 msg = "Instagram login required for comments. Run 'python setup_instagram.py' in the terminal."
            
            comments_data.append([
                "System_Alert", 
                msg, 
                str(pd.Timestamp.now())
            ])

        # Save to CSV
        df = pd.DataFrame(comments_data, columns=["author", "comment", "date"])
        
        if not os.path.exists("data"):
            os.makedirs("data")
            
        df.to_csv("data/comments.csv", index=False, encoding='utf-8')
        logger.info(f"Fetched {len(comments_data)} Instagram comments.")
        return True

    except Exception as e:
        logger.error(f"Error fetching Instagram comments: {e}")
        # If it's a login redirect (sometimes 403 or LoginRequired)
        comments_data.append([
                "System_Alert", 
                f"Error: {str(e)}. Try running 'python setup_instagram.py' to authenticate.", 
                str(pd.Timestamp.now())
        ])
        
        df = pd.DataFrame(comments_data, columns=["author", "comment", "date"])
        if not os.path.exists("data"):
            os.makedirs("data")
        df.to_csv("data/comments.csv", index=False, encoding='utf-8')
        return False
