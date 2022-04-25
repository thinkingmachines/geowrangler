# Geowrangler

## Installation

## Development

### Setting up

```
pip install pre-commit
pre-commit install
poetry install
```

### Running tests

We are using `pytest` as our test runner. To run all tests and generate a generate a coverage report, run the following.

```
poetry run pytest --cov . -n auto
```

To run a single test or test file

```
# for a single test function
poetry run pytest tests/test_grids.py::test_create_grids
# for a single test file
poetry run pytest tests/test_grids.py
```
