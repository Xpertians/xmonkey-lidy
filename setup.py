from setuptools import setup, find_packages

setup(
<<<<<<< HEAD
    name="xmonkey-lidy",
    version="1.0.0",
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
=======
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
>>>>>>> main
)
