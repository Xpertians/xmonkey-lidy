from setuptools import setup, find_packages

setup(
    name="xmonkey-lidy",
    version="1.0.4",
    description="A XMonkey tool for identifying SPDX licenses.",
    author="Oscar Valenzuela B.",
    packages=find_packages(),
    include_package_data=True,
    package_data={
        "xmonkey_lidy": ["data/*.json"]
    },
    install_requires=[
        "requests",
        "click",
        "tqdm"
    ],
    entry_points={
        "console_scripts": [
            "xmonkey-lidy=xmonkey_lidy.cli:cli"
        ]
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ],
)
