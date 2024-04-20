import click
from .analyzer import LicenseAnalyzer

@click.group()
def cli():
    pass

@cli.command()
@click.argument('directory')
@click.argument('save_path')
def prepare_dataset(directory, save_path):
    analyzer = LicenseAnalyzer()
    analyzer.prepare_dataset(directory, save_path)
    click.echo(f"Dataset prepared and saved to {save_path}")

@cli.command()
@click.argument('text')
def analyze(text):
    analyzer = LicenseAnalyzer()
    results = analyzer.analyze_text(text)
    click.echo(f"Analysis Results: {results}")

if __name__ == "__main__":
    cli()
