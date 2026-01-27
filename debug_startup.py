import sys
print("Step 1: Starting imports...", flush=True)
try:
    import flask
    print("Step 2: Flask imported", flush=True)
    import nltk
    print("Step 3: NLTK imported", flush=True)
    from src.predict import predict_sentiment
    print("Step 4: Predict module imported", flush=True)
except Exception as e:
    print(f"Error occurred: {e}", flush=True)
print("Startup Check Complete", flush=True)
