# test

## Overview

test cookiecutter

## Features

- Environment-specific configurations (dev/uat/prd)
- Athena integration for secure configuration management
- Logging configuration with Graylog integration
- Click-based CLI with comprehensive error handling

## Prerequisites

- Python 3.10 or 3.11
- Athena client secret (set as environment variable `ATHENA_SECRET`)
- Access to VUIT PyPI index for internal dependencies

## Installation

```bash
# Install project dependencies
pip install -r requirements.txt

# Or install directly from pyproject.toml
pip install -e .

# Install with development tools (ruff, pytest, etc.)
pip install -e ".[dev]"
```

## Environment Setup

Before running the application, ensure you have the required environment variable:

```bash
export ATHENA_SECRET="your-athena-client-secret"
```

## Usage

### Command Line Interface

```bash
# Get help and see all available options
python src/python/main.py --help

# Run with development environment and academic team
python src/python/main.py --env dev --team acad

# Run with UAT environment and identity team
python src/python/main.py --env uat --team ident

# Run with production environment and admin solutions team
python src/python/main.py --env prd --team admsol
```

### Available Options

- `--env`: Environment (`dev`, `uat`, `prd`) - defaults to `dev`
- `--team`: Team name (`acad`, `admsol`, `ident`) - required for Athena access

## Development

### Local Testing

For local development, you can use the included `log-config.yaml` file which will be automatically detected and used instead of the production logging configuration.

### Running Tests

|Test Type|Command|Description|
|--|--|--|
|Unit tests|`pytest src/test/unit`|Fast tests that don't require external dependencies|
|Integration tests|`pytest src/test/int` |Tests that verify end-to-end functionality|
|All tests|`pytest src/test` |Complete test suite|
|Unit tests (by marker)|`pytest -m unit`|Alternative way to run unit tests|
|Integration tests (by marker)|`pytest -m integration`|Alternative way to run integration tests|

### Code Quality

```bash
# Format code with ruff
ruff format

# Lint code with ruff
ruff check

# Fix auto-fixable linting issues
ruff check --fix

# Run both linting and formatting
ruff check --fix && ruff format
```


### Coverage Testing
```bash
# Run tests with coverage report
pytest src/test/ --cov=src/python --cov-report=term

# Generate HTML coverage report
pytest src/test/ --cov=src/python --cov-report=html

# Generate XML coverage report (for CI)
pytest src/test/ --cov=src/python --cov-report=xml

# Run coverage with all report formats
pytest src/test/ --cov=src/python --cov-report=term --cov-report=html --cov-report=xml
```


### Directory Structure

```
test
├── build-metadata.json                               # Build and deployment metadata
├── Dockerfile                                        # Container configuration
├── log-config.yaml                                   # Local logging configuration
├── README.md
├── requirements.txt                                  # Python dependencies
└── src
    ├── python
    │   └── main.py                                   # Main application entry point
    └── test
        ├── int                                       # Integration tests
        │   └── test_end_to_end.py
        │   └── test_environments.py
        │   └── test_error_scenarios.py
        │   └── test_logging_integration.py
        └── unit                                      # Unit tests
            └── test_cli.py
            └── test_logging.py
            └── test_main.py
```

## Troubleshooting

### Common Issues

**"Can't get athena properties" error:**
- Verify `ATHENA_SECRET` environment variable is set
- Ensure you have network access to Athena (beta-athena.app.vanderbilt.edu / athena.app.vanderbilt.edu)
- Check that your team parameter matches your Athena permissions

**Import errors:**
- Ensure you have access to the [VUIT PyPI](https://devops.app.vanderbilt.edu/confluence/x/HILkBw) index
- Verify all dependencies are installed: `pip install -r requirements.txt`

**Logging not appearing:**
- Check if `log-config.yaml` exists and is valid YAML
- Verify [Graylog](https://vulogs.app.vanderbilt.edu/) connectivity if using production logging
- Try looking for you logs in graylog with [this query](https://vulogs.app.vanderbilt.edu/search?rangetype=relative&fields=message%2Csource&width=1677&highlightMessage=&relative=300&q=appName%3Atest)
