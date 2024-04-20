from setuptools import setup, find_packages

setup(
    name='xmonkey-lidy',
    version='1.0',
    packages=find_packages(),
    install_requires=['click', 'spacy', 'pandas'],
    entry_points='''
        [console_scripts]
        xmonkey-lidy=xmonkey_lidy.cli:cli
    ''',
)
