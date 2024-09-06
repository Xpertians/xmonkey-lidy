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

def contains_keywords(paragraph, keywords):
    return any(keyword in paragraph for keyword in keywords)

def scan_document(filepath):
    # Load the trained model
    model = joblib.load('trained_model.pkl')
    config = json.load(open('config.json'))

    # Read the document
    with open(filepath, 'r') as file:
        text = file.read()
        # Split text by periods, commas, and end of lines
        paragraphs = [p.strip() for p in re.split(r'[.,\n\n]+', text) if p.strip() != '']

    # Analyze each paragraph
    results = {}
    for paragraph in paragraphs:
        if 'licensor' in paragraph.lower() or contains_keywords(paragraph, config['obligations'] + config['grants']):
            # Preprocess paragraph if needed
            # prediction = model.predict([preprocess(paragraph)])[0]
            prediction = model.predict([paragraph])[0]  # Assuming no preprocessing is needed
            if prediction in ['obligation', 'grant']:
                results[paragraph] = prediction

    # Print or process results as needed
    for para, tag in results.items():
        print(f"Tag: {tag}, Paragraph: {para}")  # Print first 60 characters for brevity
