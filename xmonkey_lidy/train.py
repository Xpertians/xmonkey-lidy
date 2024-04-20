import json
import os
import re
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import make_pipeline
from sklearn.model_selection import train_test_split
import joblib

nltk.download('punkt')
nltk.download('stopwords')
stop_words = list(set(stopwords.words('english')))  # Convert set to list

def contains_complex_keywords(paragraph, keyword_groups):
    for group in keyword_groups:
        if all(word in paragraph for word in group.split()):
            return True
    return False

def train_model(directory):
    config = json.load(open('config.json'))
    dataset = []

    for filename in os.listdir(directory):
        if filename.endswith('.txt'):
            path = os.path.join(directory, filename)
            with open(path, 'r') as file:
                text = file.read()
                paragraphs = [p.strip() for p in re.split(r'[.\n\n]+', text) if p.strip() != '']
                for paragraph in paragraphs:
                    if contains_complex_keywords(paragraph.lower(), config['conditional_obligations']):
                        dataset.append((paragraph, 'conditional_obligation'))
                    elif contains_complex_keywords(paragraph.lower(), config['conditional_grants']):
                        dataset.append((paragraph, 'conditional_grant'))
                    elif contains_complex_keywords(paragraph.lower(), config['complex_obligations']):
                        dataset.append((paragraph, 'obligation'))
                    elif any(word in paragraph for word in config['obligations']):
                        dataset.append((paragraph, 'obligation'))
                    elif any(word in paragraph for word in config['grants']):
                        dataset.append((paragraph, 'grant'))

    X, y = zip(*dataset)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=42)
    model = make_pipeline(TfidfVectorizer(stop_words=stop_words), MultinomialNB())
    model.fit(X_train, y_train)
    joblib.dump(model, 'trained_model.pkl')
    print("Model accuracy on test set:", model.score(X_test, y_test))
