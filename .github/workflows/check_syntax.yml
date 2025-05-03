name: Check Checks

on: [push]

permissions:
  contents: read

jobs:
  build:

    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v3
    - name: Set up Python 3.10
      uses: actions/setup-python@v4
      with:
        python-version: "3.12"

    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install flake8 pyright
        if [ -f requirements.txt ]; then pip install -r requirements.txt; fi

    - name: Check Typing with pyright
      run: pyright

    - name: Lint with flake8
      run: flake8 . --count --max-line-length=999 --statistics

    - name: Lint with flake8
      run: flake8 . --count --max-line-length=999 --statistics
