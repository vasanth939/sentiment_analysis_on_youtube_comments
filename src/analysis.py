import nltk
from collections import Counter
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import pandas as pd

# Ensure necessary NLTK data is downloaded
nltk.download('punkt', quiet=True)
nltk.download('punkt_tab', quiet=True)
nltk.download('stopwords', quiet=True)

def generate_narrative(counts, comments_list):
    """
    Generates a narrative summary based on sentiment counts and common keywords.
    
    Args:
        counts (dict): {'Positive': int, 'Negative': int, 'Neutral': int}
        comments_list (list): List of comment strings
    
    Returns:
        str: A paragraph summarizing the sentiment.
    """
    total = sum(counts.values())
    if total == 0:
        return "No comments available to analyze."

    # specific logic for majority sentiment
    dominant_sentiment = max(counts, key=counts.get)
    percentage = (counts[dominant_sentiment] / total) * 100
    
    # Keyword extraction
    all_text = " ".join([str(c) for c in comments_list]).lower()
    tokens = word_tokenize(all_text)
    stop_words = set(stopwords.words('english'))
    # Add some common youtube noise words
    stop_words.update(['video', 'youtube', 'clip', 'watching', 'watch', 'like', 'comment', 'http', 'https', 'com'])
    
    keywords = [word for word in tokens if word.isalnum() and word not in stop_words and len(word) > 3]
    common_words = Counter(keywords).most_common(5)
    top_topics = ", ".join([f"'{w[0]}'" for w in common_words])

    narrative = f"The overall sentiment for this video is predominantly **{dominant_sentiment}** ({percentage:.1f}%). "
    
    if dominant_sentiment == "Positive":
        narrative += "Viewers seem to be responding very well to the content. "
    elif dominant_sentiment == "Negative":
        narrative += "There appears to be some criticism or negative feedback in the comments. "
    else:
        narrative += "The reaction is mixed or neutral. "

    if top_topics:
        narrative += f"Frequent topics mentioned include {top_topics}."
    else:
        narrative += "No specific topics stood out significantly."

    return narrative

def get_common_words(comments_list, top_n=50):
    """
    Extracts most common words for a word cloud.
    """
    if not comments_list:
        return []

    all_text = " ".join([str(c) for c in comments_list]).lower()
    tokens = word_tokenize(all_text)
    
    stop_words = set(stopwords.words('english'))
    stop_words.update(['video', 'youtube', 'clip', 'watching', 'watch', 'like', 'comment', 'http', 'https', 'com', 'really', 'would', 'this', 'that'])
    
    # Filter keywords
    keywords = [word for word in tokens if word.isalnum() and word not in stop_words and len(word) > 2]
    
    # Count frequency
    word_counts = Counter(keywords).most_common(top_n)
    
    # Format for WordCloud [[word, size], ...]
    return [{"word": w[0], "weight": w[1]} for w in word_counts]

def get_sentiment_trend(results):
    """
    Aggregates sentiment over time.
    Automatically adjusts granularity (Day, Hour, Minute) based on time span.
    results: List of dicts with 'date' and 'sentiment'
    Returns: Lists of dates, pos_counts, neg_counts, neu_counts for Chart.js
    """
    if not results:
        return [], [], [], []

    # Convert to DataFrame
    df = pd.DataFrame(results)
    
    # Ensure date parsing
    try:
        df['datetime'] = pd.to_datetime(df['date'], errors='coerce', utc=True)
        # Drop rows with invalid dates
        df = df.dropna(subset=['datetime'])
    except Exception:
        return [], [], [], []

    if df.empty:
        return [], [], [], []

    # Determine time span
    min_time = df['datetime'].min()
    max_time = df['datetime'].max()
    time_span = max_time - min_time

    # Adaptive Grouping
    time_span_seconds = time_span.total_seconds()

    if time_span_seconds < 60: # Less than 1 minute -> Group by Second
        df['time_group'] = df['datetime'].dt.strftime('%H:%M:%S')
    elif time_span_seconds < 21600: # Less than 6 hours -> Group by Minute (better for live streams)
        df['time_group'] = df['datetime'].dt.strftime('%H:%M')
    elif time_span_seconds < 86400 * 3: # Less than 3 days -> Group by Hour
        df['time_group'] = df['datetime'].dt.strftime('%Y-%m-%d %H:00')
    else: # Default -> Group by Date
        df['time_group'] = df['datetime'].dt.strftime('%Y-%m-%d')

    # Group by time_group and Sentiment
    trend = df.groupby(['time_group', 'sentiment']).size().unstack(fill_value=0)
    
    # Ensure columns exist
    if 'Positive' not in trend.columns: trend['Positive'] = 0
    if 'Negative' not in trend.columns: trend['Negative'] = 0
    if 'Neutral' not in trend.columns: trend['Neutral'] = 0
    
    # Sort by date/time
    trend = trend.sort_index()
    
    dates = [str(d) for d in trend.index]
    pos = trend['Positive'].tolist()
    neg = trend['Negative'].tolist()
    neu = trend['Neutral'].tolist()
    
    return dates, pos, neg, neu
