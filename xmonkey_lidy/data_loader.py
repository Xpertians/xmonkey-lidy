import os

def load_texts_from_directory(directory):
    texts = {}
    for filename in os.listdir(directory):
        if filename.endswith(".txt"):
            filepath = os.path.join(directory, filename)
            with open(filepath, 'r', encoding='utf-8') as file:
                texts[filename] = file.read()
    return texts
