import re
import nltk
from nltk.corpus import stopwords

# Download stopwords only once
nltk.download("stopwords")

def clean_text(text):
    text = text.lower()
    text = re.sub(r"http\S+", "", text)
    text = re.sub(r"[^a-z\s]", "", text)

    words = text.split()
    words = [w for w in words if w not in stopwords.words("english")]

    return " ".join(words)
