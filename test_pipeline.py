from src.predict import predict_sentiment
from src.preprocess import normalize_text

examples = [
    "I am sooo happyyy today!!!",
    "This movie is baaad"
]

for example in examples:
    print(f"Input: {example}")
    print(f"Normalized text: {normalize_text(example)}")
    res = predict_sentiment(example)
    print(f"Predicted Sentiment: {res['label']}")
    print("-" * 30)
