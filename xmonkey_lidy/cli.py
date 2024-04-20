import click
from .train import train_model
from .scan import scan_document

@click.group()
def main():
    pass

@main.command()
@click.argument('directory')
def train(directory):
    """Train the model using texts in the specified directory."""
    train_model(directory)

@main.command()
@click.argument('filepath')
def scan(filepath):
    """Scan a document to identify obligations and grants."""
    scan_document(filepath)

if __name__ == '__main__':
    main()
