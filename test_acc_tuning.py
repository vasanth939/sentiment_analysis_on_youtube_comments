import sys
import os

# Add project root to sys.path
sys.path.append(os.path.abspath(r"c:\Users\vasan\OneDrive\Attachments\Desktop\youtube_ sentiment_ analysis"))

import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.svm import LinearSVC
from sklearn.naive_bayes import MultinomialNB
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
from src.preprocess import clean_text

def find_best_model():
    df = pd.read_csv(r"c:\Users\vasan\OneDrive\Attachments\Desktop\youtube_ sentiment_ analysis\data\training_dataset.csv")
    df['Sentiment'] = df['Sentiment'].astype(str).str.lower()
    df = df[df['Sentiment'].isin(['positive', 'negative'])]
    df['label'] = df['Sentiment'].map({'positive': 1, 'negative': 0})
    
    print("Cleaning text...")
    df['cleaned_text'] = df['Comment'].astype(str).apply(clean_text)
    
    # Try different TF-IDF configs
    configs = [
        {'max_features': 5000, 'ngram_range': (1, 2)},
        {'max_features': 10000, 'ngram_range': (1, 2)},
        {'max_features': 15000, 'ngram_range': (1, 3)},
        {'max_features': 20000, 'ngram_range': (1, 3), 'min_df': 2, 'max_df': 0.9},
    ]
    
    models = {
        'LogisticRegression': LogisticRegression(max_iter=1000),
        'LogisticRegression_C2': LogisticRegression(C=2.0, max_iter=1000),
        'LogisticRegression_C5': LogisticRegression(C=5.0, max_iter=1000),
        'LinearSVC': LinearSVC(random_state=42),
        'LinearSVC_C0.5': LinearSVC(C=0.5, random_state=42),
        'LinearSVC_C0.1': LinearSVC(C=0.1, random_state=42),
    }

    best_acc = 0
    best_config = None
    best_model = None

    for i, config in enumerate(configs):
        print(f"\nEvaluating TF-IDF Config {i}: {config}")
        vectorizer = TfidfVectorizer(**config)
        X = vectorizer.fit_transform(df['cleaned_text'])
        y = df['label']
        
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        for model_name, model in models.items():
            model.fit(X_train, y_train)
            y_pred = model.predict(X_test)
            acc = accuracy_score(y_test, y_pred)
            print(f"- {model_name}: {acc:.4f}")
            if acc > best_acc:
                best_acc = acc
                best_config = config
                best_model = model_name

    print("\n=================")
    print(f"BEST RESULT: {best_acc:.4f}")
    print(f"BEST CONFIG: {best_config}")
    print(f"BEST MODEL: {best_model}")

if __name__ == "__main__":
    find_best_model()
