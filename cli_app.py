from src.fetch_comments import fetch_comments
from src.predict import predict_sentiment
import pandas as pd
import matplotlib.pyplot as plt
import sys

# Force UTF-8 encoding for console output (handles emojis on Windows)
sys.stdout.reconfigure(encoding='utf-8')

print("YouTube Sentiment Analysis Started")

video_url = input("Enter YouTube Video URL: ")

fetch_comments(video_url)

df = pd.read_csv("data/comments.csv")

sentiment_count = {
    "Positive": 0,
    "Negative": 0,
    "Neutral": 0
}

# Lists to store detailed comments
details = {
    "Positive": [],
    "Negative": [],
    "Neutral": []
}

for comment, author in zip(df["comment"], df["author"]):
    prediction = predict_sentiment(str(comment))
    sentiment = prediction['label']
    confidence = prediction['confidence']
    
    sentiment_count[sentiment] += 1
    details[sentiment].append(f"{author}: {comment} (Confidence: {confidence}%)")

print("\nSentiment Results:")
for k, v in sentiment_count.items():
    print(f"{k}: {v}")

print("\n--- Detailed Comments ---")
for category in ["Positive", "Negative", "Neutral"]:
    print(f"\n[{category} Comments]")
    if not details[category]:
        print("  (None)")
    else:
        # Show up to 5 examples to avoid flooding the terminal
        for item in details[category][:10]: 
            print(f"  - {item}")
        if len(details[category]) > 10:
            print(f"  ... and {len(details[category]) - 10} more.")

plt.bar(sentiment_count.keys(), sentiment_count.values(), color=['green', 'red', 'gray'])
plt.title("YouTube Comment Sentiment Analysis")
plt.xlabel("Sentiment")
plt.ylabel("Number of Comments")
plt.show()
