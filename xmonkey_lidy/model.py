def tag_paragraph(paragraph, config):
    # Simple tagging based on keyword presence
    for obligation in config['obligations']:
        if obligation in paragraph:
            return {'text': paragraph, 'tag': 'obligation'}
    for grant in config['grants']:
        if grant in paragraph:
            return {'text': paragraph, 'tag': 'grant'}
    return None
