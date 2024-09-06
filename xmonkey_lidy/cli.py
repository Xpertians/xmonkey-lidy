import click
from .downloader import LicenseDownloader
from .matcher import LicenseMatcher

@click.group()
def cli():
    """Command-line interface for xmonkey-lidy."""
    pass

@click.command()
def update():
    """Download and replace SPDX licenses and generate JSON files."""
    downloader = LicenseDownloader()
    downloader.download_and_update_licenses()

@click.command()
@click.argument("file")
def identify(file):
    """Identify the license using patterns or Sørensen-Dice."""
    matcher = LicenseMatcher()
    result = matcher.identify_license(file)
    click.echo(result)

@click.command()
@click.argument("spdx", required=False)
def validate(spdx):
    """Validate pattern matching for a specific SPDX or all SPDX licenses."""
    matcher = LicenseMatcher()
    result = matcher.validate_patterns(spdx)
    click.echo(result)

@click.command()
@click.argument("spdx")
def produce(spdx):
    """Produce a copy of the specified SPDX license."""
    matcher = LicenseMatcher()
    license_text = matcher.produce_license(spdx)
    click.echo(license_text)

cli.add_command(update)
cli.add_command(identify)
cli.add_command(validate)
cli.add_command(produce)