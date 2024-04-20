from setuptools import setup, find_packages

setup(
    name='xmonkey_lidy',
    version='0.1.0',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'click',
        'nltk',
        'scikit-learn',
    ],
    entry_points={
        'console_scripts': [
            'xmonkey-lidy = xmonkey_lidy.cli:main',
        ],
    },
)
