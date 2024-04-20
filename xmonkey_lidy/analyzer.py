from .utils import extract_paragraphs, tag_paragraphs, save_data, load_data
from .data_loader import load_texts_from_directory
import spacy

class LicenseAnalyzer:
    def __init__(self):
        self.nlp = spacy.load("en_core_web_sm")
        self.keywords = {
            'obligation': ['must', 'shall', 'is required to'],
            'permission': ['may', 'is permitted to', 'is allowed to']
        }

    def prepare_dataset(self, directory, save_path):
        texts = load_texts_from_directory(directory)
        dataset = {}
        for filename, text in texts.items():
            paragraphs = extract_paragraphs(text)
            tagged_paragraphs = tag_paragraphs(paragraphs, self.keywords)
            dataset[filename] = tagged_paragraphs
        save_data(dataset, save_path)
        return dataset

    def analyze_text(self, text):
        doc = self.nlp(text)
        results = {'obligations': [], 'permissions': []}
        for ent in doc.ents:
            if ent.label_.upper() in self.keywords['obligation']:
                results['obligations'].append(ent.text)
            elif ent.label_.upper() in self.keywords['permission']:
                results['permissions'].append(ent.text)
        return results
