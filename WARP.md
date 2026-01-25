# WARP.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

## Project Overview

Python AbraFlexi is a Python 3.8+ library for easy interaction with the Czech economic system AbraFlexi. This is a Python port of the PHP AbraFlexi library, providing a complete REST API client with object-oriented interface for all AbraFlexi evidences (entities).

## Development Commands

### Package Management

```bash
pip install -e .              # Install in development mode
pip install -e ".[dev]"       # Install with development dependencies
pip install -r requirements.txt  # Install requirements only
```

### Testing

```bash
pytest                        # Run all tests
pytest tests/test_read_only.py  # Run specific test file
pytest -v                     # Verbose output
pytest --cov                  # With coverage report
```

### Code Quality

```bash
black python_abraflexi/       # Format code with Black
flake8 python_abraflexi/      # Lint code
mypy python_abraflexi/        # Type checking
```

### Building

```bash
python setup.py sdist bdist_wheel  # Build distribution packages
dpkg-buildpackage -us -uc          # Build Debian package
```

## Core Architecture

### Class Hierarchy

The library follows a layered architecture with these core base classes:

- **`ReadOnly`**: Base class for reading data from AbraFlexi
  - Located: `python_abraflexi/read_only.py`
  - Handles HTTP communication, authentication, and data parsing
  - Contains request operations, URL building, and response processing

- **`ReadWrite`**: Extends ReadOnly for write operations
  - Located: `python_abraflexi/read_write.py`
  - Adds insert, update, delete functionality
  - Supports transactions (`atomic` mode) and dry-run testing

### Evidence System

AbraFlexi uses "evidences" (entities/records). Each evidence should have:
- Custom class derived from ReadOnly or ReadWrite
- Class naming: evidence name in PascalCase (e.g., `faktura-vydana` → `FakturaVydana`)
- Each class sets `evidence` property in constructor

### Configuration

Connection can be configured via:
1. Constructor parameters (highest priority)
2. Environment variables: `ABRAFLEXI_URL`, `ABRAFLEXI_LOGIN`, `ABRAFLEXI_PASSWORD`, `ABRAFLEXI_COMPANY`
3. Default values

### Data Types

The library automatically converts AbraFlexi data types to Python equivalents:
- `date` → `datetime.date`
- `datetime` → `datetime.datetime`
- `integer` → `int`
- `numeric` → `float`
- `logic` → `bool`
- `relation` → `Relation` object

## Testing Infrastructure

### Test Configuration
- Test framework: pytest
- Tests located in: `tests/`
- Test server: Uses demo.flexibee.eu by default, configurable via environment variables

### Test Structure
- Unit tests in `tests/`
- Each main class should have corresponding test file
- Tests should use fixtures for common setup

## Code Standards

### From Project Guidelines:
- **Python Version**: Python 3.8 or later
- **Code Style**: PEP 8 with Black formatter (88 char line length)
- **Documentation**: Include docstrings for all functions and classes with parameters and return types
- **Type Hints**: Use type hints for parameters and return types where practical
- **Testing**: Create/update pytest tests for new/modified classes
- **Comments**: Write in English using complete sentences
- **Variables**: Use meaningful, descriptive names (snake_case for functions/variables)
- **Constants**: Use UPPERCASE for constants
- **Error Handling**: Handle exceptions properly with specific exception types

### Code Formatting
The project uses Black formatter with 88 character line length.

## Project Structure

```
python_abraflexi/          # Main library package
├── __init__.py            # Package initialization
├── read_only.py           # Base read-only class
├── read_write.py          # Base read-write class
├── exceptions.py          # Custom exceptions
├── relation.py            # Relation handling
└── evidences/             # Evidence-specific classes (future)

examples/                  # Usage examples
tests/                     # Pytest tests
debian/                    # Debian packaging files
docs/                      # Documentation
```

## Important Implementation Notes

### Evidence Class Creation Pattern

```python
from python_abraflexi import ReadWrite

class FakturaVydana(ReadWrite):
    """Issued invoice evidence."""
    
    def __init__(self, init=None, options=None):
        if options is None:
            options = {}
        options['evidence'] = 'faktura-vydana'
        super().__init__(init, options)
```

### Object Instantiation with Options

```python
from python_abraflexi import ReadWrite

invoice = ReadWrite('code:VF2-12345', {
    'company': 'demo',
    'url': 'https://demo.flexibee.eu',
    'user': 'winstrom',
    'password': 'winstrom',
    'debug': True,
    'native_types': False,  # Disable automatic type conversion
    'ignore404': True       # Don't throw exception for missing records
})
```

### Authentication Methods
1. Username/password (HTTPBasicAuth)
2. AuthSessionId for web application integration
3. Environment variables

### Debug Mode Features
- Validates field existence and permissions
- Logs all requests/responses
- Enhanced error messages for development
- Pretty-printed JSON in requests

## Dependencies

### Runtime
- Python 3.8+
- requests >= 2.28.0
- python-dateutil >= 2.8.0
- urllib3 >= 1.26.0

### Development
- pytest >= 7.0
- pytest-cov >= 3.0
- black >= 22.0
- flake8 >= 4.0
- mypy >= 0.950

## License

MIT License - allows commercial use and modification.

## Conversion Notes

This project was converted from the PHP AbraFlexi library. Key differences:
- PHP classes → Python classes
- Composer → pip/setuptools
- PHPUnit → pytest
- PHP arrays → Python dicts/lists
- PHP exceptions → Python exceptions
- camelCase → snake_case (for Python methods)
