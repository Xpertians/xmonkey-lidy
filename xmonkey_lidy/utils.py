import json
import re

def extract_paragraphs(text):
    # Normalize space characters and remove unwanted characters
    # Replace non-alphanumeric and non-colon characters with a space, except for periods and newlines
    cleaned_text = re.sub(r'[^a-zA-Z0-9:\s\.]', ' ', text)
    # Reduce multiple spaces to a single space
    cleaned_text = re.sub(r'\s+', ' ', cleaned_text)
    # Split the text at each period followed by a space or a double newline
    paragraphs = re.split(r'\.\s+|\n\n+', cleaned_text)
    # Further clean each paragraph to remove trailing or leading spaces
    return [paragraph.strip() for paragraph in paragraphs if paragraph.strip()]


def tag_paragraphs(paragraphs, keywords):
    tagged = []
    for paragraph in paragraphs:
        tags = {'OBLIGATION': any(key in paragraph for key in keywords['obligation']),
                'PERMISSION': any(key in paragraph for key in keywords['permission'])}
        tagged.append((paragraph, tags))
    return tagged

def save_data(data, filepath):
    with open(filepath, 'w', encoding='utf-8') as file:
        json.dump(data, file)

def load_data(filepath):
    with open(filepath, 'r', encoding='utf-8') as file:
        return json.load(file)
