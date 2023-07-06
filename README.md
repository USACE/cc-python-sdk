# cc-python-sdk

[![PyPI version](https://badge.fury.io/py/cc-python-sdk.svg)](https://badge.fury.io/py/cc-python-sdk)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

cc-python-sdk is the Python Software Development Kit used to develop plugins for Cloud Compute.

## Installation

You can install cc-python-sdk in two ways: from source or through the pip package manager.

### Installing from source

To install cc-python-sdk from source, follow these steps:

1. Clone the repository:

```shell
git clone https://github.com/USACE/cc-python-sdk.git
```

2. Navigate to the project directory:

```shell
cd cc-python-sdk
```

3. Create a virtual environment (optional but recommended):

```shell
python3 -m venv venv
source venv/bin/activate
```

4. Install the package dependencies:

```shell
pip install -r requirements.txt
```

5. Install the build dependencies

```shell
python3 -m pip install --upgrade build
```

6. Build cc-python-sdk from the `pyproject.toml`:

```shell
python3 -m build
```

7. Install the generated wheel (replace <version> with the version of the wheel file built):

```shell
pip install dist/cc_python_sdk-<version>-py3-none-any.whl
```

or 

```shell
pip install dist/*.whl
```

Now you have successfully installed cc-python-sdk from source.

## Install from pre-built distribution

Download the release from the 'Releases' page of this repository, then install with pip:

```shell
pip install <path/to/wheel/*.whl>
```

### Installing through pip

To install cc-python-sdk using pip, simply run the following command:

```shell
pip install cc-python-sdk
```

This will download the latest version of cc-python-sdk from the Python Package Index (PyPI) and install it into your Python environment.

## Usage

Once cc-python-sdk is installed, you can start using its functionality in your Python projects. Here's a simple example:

```python
import cc_sdk

# Use the functions and classes provided by cc_sdk
```

## Documentation

TODO. See example plugin [here](https://<>)
