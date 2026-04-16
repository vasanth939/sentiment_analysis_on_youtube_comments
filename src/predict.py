import joblib
import numpy as np
import warnings
from src.preprocess import normalize_text, clean_text

# Suppress sklearn warnings about feature names
warnings.filterwarnings("ignore", category=UserWarning)

print("Loading ML Sentiment Analysis Models...")
model = joblib.load("model/sentiment_model.pkl")
vectorizer = joblib.load("model/vectorizer.pkl")

def predict_sentiment(comment):
    text = str(comment)
    text = normalize_text(text)
    text = clean_text(text)
    
    # Handle empty text after processing
    if not text.strip():
        return {"label": "Neutral", "score": 0.0, "confidence": 0.0}
    
    X = vectorizer.transform([text])
    
    try:
        # LinearSVC prediction
        pred = model.predict(X)[0]
        decision = model.decision_function(X)[0]
        
        # Binary Classification mapping
        if pred == 1:
            label = "Positive"
        else:
            label = "Negative"
            
        # Sigmoid probability calculation for confidence
        prob = 1 / (1 + np.exp(-decision))
        
        if label == "Positive":
            confidence = prob * 100
            score = decision
        else:
            confidence = (1 - prob) * 100
            score = decision
            
        # Optional neutral threshold based on distance to decision boundary
        if abs(decision) < 0.2:
            label = "Neutral"
            
    except Exception as e:
        print(f"Error during prediction: {e}")
        return {"label": "Neutral", "score": 0.0, "confidence": 0.0}
        
    return {
        "label": label,
        "score": float(score),
        "confidence": round(float(confidence), 1)
    }
