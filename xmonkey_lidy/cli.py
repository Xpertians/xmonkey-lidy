import click
from .downloader import LicenseDownloader
from .matcher import LicenseMatcher


@click.group()
def cli():
    """Command-line interface for xmonkey-lidy."""
    pass


@click.command()
@click.option(
    '--publisher',
    default="Official Rules Publisher",
    help="Publisher name for the generated data."
)
@click.option(
    '--data-dir',
    default="data",
    help="Directory where JSON files will be stored."
)
def update(publisher, data_dir):
    """Download and replace SPDX licenses and generate JSON files."""
    downloader = LicenseDownloader(publisher=publisher, data_dir=data_dir)
    downloader.download_and_update_licenses()


@click.command()
@click.argument("file")
@click.option(
    '--use-soredice-only',
    is_flag=True,
    help="Only use Sørensen-Dice for matching."
)
@click.option(
    '--debug',
    is_flag=True,
    help="Show debug information for all licenses."
)
def identify(file, use_soredice_only, debug):
    """Identify the license using patterns or Sørensen-Dice."""
    matcher = LicenseMatcher()
    result = matcher.identify_license(
        file, use_soredice_only=use_soredice_only, debug=debug
    )
    click.echo(result)


@click.command()
@click.argument("file")
@click.argument("spdx", required=False)
def validate(file, spdx):
    """Validate the license file against specific or all SPDX patterns."""
    matcher = LicenseMatcher()
    result = matcher.validate_patterns(file, spdx)
    click.echo(result)


@click.command()
@click.argument("spdx")
def produce(spdx):
    """Produce a copy of the specified SPDX license."""
    matcher = LicenseMatcher()
    license_text = matcher.produce_license(spdx)
    click.echo(license_text)


@click.command()
@click.argument("file")
def extract_copyright(file):
    """Extract copyright information from a provided text file."""
    matcher = LicenseMatcher()
    result = matcher.extract_copyright_info_from_file(file)
    click.echo(result)


cli.add_command(update)
cli.add_command(identify)
cli.add_command(validate)
cli.add_command(produce)
cli.add_command(extract_copyright)
