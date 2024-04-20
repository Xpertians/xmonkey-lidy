import json

def extract_paragraphs(text):
    return text.split('\n\n')

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
