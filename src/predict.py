from nltk.sentiment.vader import SentimentIntensityAnalyzer
import nltk

# Download VADER lexicon (only needs to be done once)
# Download VADER lexicon (only needs to be done once)
print("Loading Sentiment Analysis Models...")
nltk.download('vader_lexicon', quiet=True)

sid = SentimentIntensityAnalyzer()

def predict_sentiment(comment):
    # VADER works best with raw text
    scores = sid.polarity_scores(comment)
    compound = scores['compound']
    
    # Calculate confidence as the highest probability among pos, neg, neu
    # This gives a "how sure is VADER this is X" metric
    # Note: 'compound' is a normalized metric, 'pos'/'neg'/'neu' are ratios
    confidence = max(scores['pos'], scores['neg'], scores['neu']) * 100
    
    if compound >= 0.05:
        label = "Positive"
    elif compound <= -0.05:
        label = "Negative"
    else:
        label = "Neutral"
        
    return {
        "label": label,
        "score": compound,
        "confidence": round(confidence, 1)
    }
