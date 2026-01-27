import pandas as pd
import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score
from src.preprocess import clean_text

def train():
    print("Loading data...")
    # Load dataset
    df = pd.read_csv("data/comments.csv")
    
    # Check if 'Sentiment' column exists
    if 'Sentiment' not in df.columns:
        print("Error: 'Sentiment' column not found in data/comments.csv")
        return

    # Filter for Positive/Negative only
    df['Sentiment'] = df['Sentiment'].astype(str).str.lower()
    df = df[df['Sentiment'].isin(['positive', 'negative'])]
    
    # Map to 0/1
    df['label'] = df['Sentiment'].map({'positive': 1, 'negative': 0})
    
    print("Preprocessing text...")
    df['cleaned_text'] = df['Comment'].astype(str).apply(clean_text)
    
    # Vectorization (TF-IDF is better for sentiment)
    vectorizer = TfidfVectorizer(max_features=5000)
    X = vectorizer.fit_transform(df['cleaned_text'])
    y = df['label']
    
    # Split
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # Train (Logistic Regression often works better with TF-IDF)
    print("Training model...")
    model = LogisticRegression()
    model.fit(X_train, y_train)
    
    # Evaluate
    y_pred = model.predict(X_test)
    print(f"Accuracy: {accuracy_score(y_test, y_pred)}")
    
    # Save
    print("Saving model and vectorizer...")
    joblib.dump(model, "model/sentiment_model.pkl")
    joblib.dump(vectorizer, "model/vectorizer.pkl")
    print("Done!")

if __name__ == "__main__":
    train()
