# xmonkey-lidy

`xmonkey-lidy` is a command-line and Python library tool for identifying open-source licenses in text files using Sørensen-Dice proximity matching and pattern-based matching. It supports SPDX license detection with debug options to help investigate how matches were made.

## Features

- Identify open-source licenses in files using Sørensen-Dice similarity or pattern matching.
- Validate files against specific SPDX licenses.
- Download and update the SPDX license data.
- Generate detailed debug information showing matched and excluded patterns.

## Installation

### Prerequisites

- Python 3.8 or higher
- `pip3` (Python package installer)

### Installing with `pip3`

You can install the tool directly using `pip3`:

```bash
pip3 install xmonkey-lidy
```

Once installed, the `xmonkey-lidy` command-line tool will be available globally.

Alternatively, if you're using a virtual environment:

```bash
python3 -m venv env
source env/bin/activate
pip3 install xmonkey-lidy
```

### Installing from Source

1. Clone the repository or download the package:

   ```bash
   git clone https://github.com/yourusername/xmonkey-lidy.git
   cd xmonkey-lidy
   ```

2. Install the package:

   ```bash
   pip3 install .
   ```

## Usage (CLI)

The following are the commands available in `xmonkey-lidy`:

### 1. Download or Update SPDX License Data

```bash
xmonkey-lidy update --data-dir <path_to_store_data> --publisher <publisher_name>
```

Example:

```bash
xmonkey-lidy update --data-dir ./data --publisher "MyCustomPublisher"
```

### 2. Identify License

```bash
xmonkey-lidy identify <path_to_file>
```

Example:

```bash
xmonkey-lidy identify ./path/to/LICENSE.txt
```

### 3. Validate License

```bash
xmonkey-lidy validate <path_to_file> <SPDX_license>
```

Example:

```bash
xmonkey-lidy validate ./path/to/LICENSE.txt Apache-2.0
```

### 4. Produce SPDX License Text

```bash
xmonkey-lidy produce <SPDX_license>
```

Example:

```bash
xmonkey-lidy produce MIT
```

## Usage in Other Libraries (Dependency)

You can use `xmonkey-lidy` as a dependency in other Python projects by including it in your `requirements.txt` or `setup.py` file.

### 1. Using `xmonkey-lidy` in `requirements.txt`

Add the following line to your `requirements.txt` file:

```
xmonkey-lidy
```

Then, install the dependencies:

```bash
pip3 install -r requirements.txt
```

### 2. Using `xmonkey-lidy` in `setup.py`

In your `setup.py`, you can add `xmonkey-lidy` as a dependency:

```python
from setuptools import setup, find_packages

setup(
    name='your_project_name',
    version='1.0',
    packages=find_packages(),
    install_requires=[
        'xmonkey-lidy'
    ],
)
```

### 3. Importing `xmonkey-lidy` in Your Code

Once installed, you can use `xmonkey-lidy` programmatically by importing the necessary classes in your Python project. For example:

```python
from xmonkey_lidy.matcher import LicenseMatcher

# Initialize the LicenseMatcher
matcher = LicenseMatcher()

# Identify the license of a file
result = matcher.identify_license('./path/to/LICENSE.txt')

# Print the result
print(result)
```

In this example, you can interact with the `LicenseMatcher` class directly and perform license identification, validation, and more within your own code.

### Example of License Validation in Python Code

```python
from xmonkey_lidy.matcher import LicenseMatcher

# Initialize the LicenseMatcher
matcher = LicenseMatcher()

# Validate a file against a specific SPDX license
validation_result = matcher.validate_patterns('./path/to/LICENSE.txt', 'Apache-2.0')

# Print validation result
print(validation_result)
```

By importing and using `xmonkey-lidy`, you can integrate license identification and validation capabilities directly into your Python projects.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.