print("Initializing YouTube Sentiment Analysis AI... This may take a moment.")
from flask import Flask, render_template, request, jsonify
from src.fetch_comments import fetch_comments, fetch_video_details
from src.predict import predict_sentiment
import pandas as pd
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    data = request.json
    video_url = data.get('url')
    
    if not video_url:
        return jsonify({"error": "No URL provided"}), 400


    try:
        # Default to YouTube Flow
        # 1. Fetch Video Metadata
        video_meta = fetch_video_details(video_url)
        if not video_meta:
             return jsonify({"error": "Invalid Video URL or Video not found"}), 404

        # 2. Fetch Transcript
        from src.fetch_transcript import fetch_transcript_text
        transcript_text = fetch_transcript_text(video_url)

        # 3. Fetch Comments
        app.logger.info(f"Fetching comments for: {video_url}")
        fetch_comments(video_url)
        
        # 4. Read Data
        if not os.path.exists("data/comments.csv"):
             return jsonify({"error": "Failed to fetch comments or content has no comments."}), 500
             
        df = pd.read_csv("data/comments.csv")
        
        # Process all fetched comments as requested by the user
        df = df.dropna(subset=['comment'])
        
        # 5. Analyze Sentiment
        results = []
        counts = {"Positive": 0, "Negative": 0, "Neutral": 0}
        comments_list_for_narrative = []
        
        # Helper to avoid NaN dates
        if 'date' not in df.columns:
            df['date'] = pd.Timestamp.now()
            
        system_alert_message = None

        for comment, author, date_posted in zip(df["comment"], df["author"], df["date"]):
            # Normalize inputs
            comment_str = str(comment)
            author_str = str(author)
            date_str = str(date_posted)
            
            # Check for System Alert
            if author_str == "System_Alert":
                system_alert_message = comment_str
            
            # Prediction
            prediction = predict_sentiment(comment_str)
            label = prediction['label']
            counts[label] += 1
            
            results.append({
                "author": author_str,
                "comment": comment_str,
                "sentiment": label,
                "confidence": prediction['confidence'],
                "score": prediction['score'],
                "date": date_str
            })
            
            comments_list_for_narrative.append(comment_str)

        # 5a. Advanced Analytics: Identify "Hall of Fame" Comments
        # Sort by score to find most positive/negative
        sorted_comments = sorted(results, key=lambda x: x['score'], reverse=True)
        top_positive = sorted_comments[0] if sorted_comments and sorted_comments[0]['score'] > 0 else None
        top_negative = sorted_comments[-1] if sorted_comments and sorted_comments[-1]['score'] < 0 else None
        
        # 5b. Advanced Analytics: Word Cloud Data
        from src.analysis import get_common_words, generate_narrative
        word_cloud_data = get_common_words(comments_list_for_narrative)
        
        # 5c. Advanced Analytics: Average Sentiment Score (0 to 100 normalized)
        # Average compound score (-1 to 1) -> mapped to 0-100
        avg_score = 0
        if results:
            total_compound = sum(r['score'] for r in results)
            avg_compound = total_compound / len(results)
            avg_score = round((avg_compound + 1) * 50, 1) # Map -1..1 to 0..100

        # 5d. Advanced Analytics: Time Series Trend
        from src.analysis import get_sentiment_trend
        dates, trend_pos, trend_neg, trend_neu = get_sentiment_trend(results)
        
        # 6. Generate Narrative
        from src.analysis import generate_narrative
        
        if system_alert_message:
            narrative = f"⚠️ SYSTEM ALERT: {system_alert_message}"
        else:
            narrative = generate_narrative(counts, comments_list_for_narrative)
            
        return jsonify({
            "meta": video_meta,
            "counts": counts,
            "comments": results,
            "transcript": transcript_text if transcript_text else "Transcript not available for this video.",
            "narrative": narrative,
            "word_cloud": word_cloud_data,
            "top_comment": top_positive,
            "worst_comment": top_negative,
            "sentiment_score": avg_score,
            "trend_dates": dates,
            "trend_pos": trend_pos,
            "trend_neg": trend_neg,
            "trend_neu": trend_neu,
            "trend_available": len(dates) > 1
        })

    except Exception as e:
        app.logger.error(f"Error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/predict_text', methods=['POST'])
def predict_text():
    data = request.json
    text = data.get('text')
    if not text:
        return jsonify({"error": "No text provided"}), 400
        
    from src.predict import predict_sentiment
    prediction = predict_sentiment(text)
    return jsonify(prediction)

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "ok"}), 200

if __name__ == '__main__':
    import os
    import webbrowser
    import threading
    
    # Create data directory if not exists
    if not os.path.exists("data"):
        os.makedirs("data")

    print("----------------------------------------------------------------", flush=True)
    print("YT SENTIMENT AI: SERVER STARTING", flush=True)
    print("----------------------------------------------------------------", flush=True)
    
    # Production Server (Waitress)
    # This removes the "Development Server" warning and is more stable
    from waitress import serve
    print("----------------------------------------------------------------", flush=True)
    print("YT SENTIMENT ANALYSIS: PRODUCTION SERVER ACTIVE", flush=True)
    print("Access the dashboard at: http://127.0.0.1:8080", flush=True)
    print("----------------------------------------------------------------", flush=True)

    # Open browser automatically
    def open_browser():
        webbrowser.open("http://127.0.0.1:8080")
        
    threading.Timer(1.5, open_browser).start()

    # Serve on port defined by environment or 8080
    port = int(os.environ.get("PORT", 8080))
    serve(app, host='0.0.0.0', port=port, threads=6)
