import re
import nltk
from nltk.corpus import stopwords
from itertools import product
from nltk.corpus import wordnet
from nltk.sentiment.vader import SentimentIntensityAnalyzer

# Download necessary NLTK data
nltk.download("stopwords", quiet=True)
nltk.download("wordnet", quiet=True)
nltk.download("vader_lexicon", quiet=True)

sid = SentimentIntensityAnalyzer()
vader_lexicon = sid.lexicon

def normalize_repeated_chars(word):
    if word in vader_lexicon or wordnet.synsets(word):
        return word
        
    matches = list(re.finditer(r'([a-z])\1+', word))
    if not matches:
        return word
        
    choices = []
    for m in matches:
        char = m.group(1)
        choices.append((char * 2, char * 1))
        
    best_candidate = word
    best_score = -1
    
    for combo in product(*choices):
        chars = []
        last_end = 0
        for i, m in enumerate(matches):
            chars.append(word[last_end:m.start()])
            chars.append(combo[i])
            last_end = m.end()
        chars.append(word[last_end:])
        
        candidate = "".join(chars)
        
        score = 0
        if candidate in vader_lexicon:
            score += 2
        if wordnet.synsets(candidate):
            score += 1
            
        if score > best_score:
            best_score = score
            best_candidate = candidate
            
    if best_score == 0:
        chars = []
        last_end = 0
        for m in matches:
            chars.append(word[last_end:m.start()])
            chars.append(m.group(1))
            last_end = m.end()
        chars.append(word[last_end:])
        return "".join(chars)
        
    return best_candidate

def normalize_text(text):
    text = str(text).lower()
    def replace_word(match):
        return normalize_repeated_chars(match.group(0))
    return re.sub(r'[a-z]+', replace_word, text)

def clean_text(text):
    text = normalize_text(text)
    text = re.sub(r"http\S+", "", text)
    text = re.sub(r"[^a-z\s]", "", text)

    words = text.split()
    
    # Explicitly keep negation words to support context-aware modeling
    negation_words = {"not", "no", "never", "hardly", "nor", "none", "neither"}
    stop_words = set(stopwords.words("english")) - negation_words
    
    words = [w for w in words if w not in stop_words]

    return " ".join(words)
