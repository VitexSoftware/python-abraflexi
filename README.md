# Python AbraFlexi

![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

Python library for easy interaction with the Czech economic system AbraFlexi (FlexiBee).

This is a Python port of the [PHP AbraFlexi library](https://github.com/Spoje-NET/php-abraflexi), providing a complete REST API client with an object-oriented interface for all AbraFlexi operations.

## Features

- **Full REST API Support**: Complete implementation of AbraFlexi REST API
- **Object-Oriented Interface**: Clean, Pythonic API design
- **Multiple Authentication Methods**: Basic auth, session ID
- **Type Conversion**: Automatic conversion between AbraFlexi and Python types
- **Transaction Support**: Atomic operations with dry-run mode
- **Batch Operations**: Efficient bulk insert/update operations
- **Comprehensive Error Handling**: Detailed exceptions for all error cases
- **Easy Configuration**: Environment variables, constructor parameters, or config files

## Installation

### From Source

```bash
git clone https://github.com/VitexSoftware/python-abraflexi.git
cd python-abraflexi
pip install -e .
```

### From PyPI (when published)

```bash
pip install python-abraflexi
```

### Debian/Ubuntu Package

```bash
sudo apt install python3-vitexsoftware-abraflexi
```

## Quick Start

### Basic Usage

```python
from python_abraflexi import ReadWrite

# Configure via constructor
invoice = ReadWrite(None, {
    'url': 'https://demo.flexibee.eu',
    'company': 'demo',
    'user': 'winstrom',
    'password': 'winstrom',
    'evidence': 'faktura-vydana'
})

# Get all invoices
invoices = invoice.get_all_from_abraflexi()
print(f"Found {len(invoices)} invoices")

# Create new invoice
new_invoice = ReadWrite(None, {
    'url': 'https://demo.flexibee.eu',
    'company': 'demo',
    'user': 'winstrom',
    'password': 'winstrom',
    'evidence': 'faktura-vydana'
})

new_invoice.set_data_value('kod', 'TEST001')
new_invoice.set_data_value('nazev', 'Test Invoice')
new_invoice.set_data_value('firma', 'code:ABCFIRM1')

result = new_invoice.insert_to_abraflexi()
print(f"Created invoice with ID: {new_invoice.last_inserted_id}")
```

### Using Environment Variables

```python
import os

os.environ['ABRAFLEXI_URL'] = 'https://demo.flexibee.eu'
os.environ['ABRAFLEXI_COMPANY'] = 'demo'
os.environ['ABRAFLEXI_LOGIN'] = 'winstrom'
os.environ['ABRAFLEXI_PASSWORD'] = 'winstrom'

from python_abraflexi import ReadOnly

# Configuration loaded from environment
invoice = ReadOnly(None, {'evidence': 'faktura-vydana'})
invoices = invoice.get_all_from_abraflexi()
```

### Loading Specific Record

```python
from python_abraflexi import ReadOnly

# Load by ID
invoice = ReadOnly(123, {
    'url': 'https://demo.flexibee.eu',
    'company': 'demo',
    'user': 'winstrom',
    'password': 'winstrom',
    'evidence': 'faktura-vydana'
})

print(f"Invoice: {invoice.get_data_value('kod')}")

# Load by code
invoice2 = ReadOnly('code:TEST001', {
    'url': 'https://demo.flexibee.eu',
    'company': 'demo',
    'user': 'winstrom',
    'password': 'winstrom',
    'evidence': 'faktura-vydana'
})
```

## Configuration

Configuration can be provided in three ways (in order of priority):

1. **Constructor parameters** (highest priority)
2. **Environment variables**
3. **Default values**

### Available Options

| Option | Environment Variable | Description |
|--------|---------------------|-------------|
| `url` | `ABRAFLEXI_URL` | AbraFlexi server URL |
| `company` | `ABRAFLEXI_COMPANY` | Company identifier |
| `user` | `ABRAFLEXI_LOGIN` | API username |
| `password` | `ABRAFLEXI_PASSWORD` | API password |
| `authSessionId` | `ABRAFLEXI_AUTHSESSID` | Session ID (alternative to user/pass) |
| `evidence` | - | Evidence name (e.g., 'faktura-vydana') |
| `timeout` | `ABRAFLEXI_TIMEOUT` | Request timeout in seconds (default: 300) |
| `debug` | - | Enable debug mode |
| `throwException` | `ABRAFLEXI_EXCEPTIONS` | Throw exceptions on errors |
| `ignore404` | - | Don't throw exception on 404 errors |
| `native_types` | - | Convert types to Python natives |
| `dry-run` | - | Test mode (doesn't save changes) |
| `atomic` | - | Transaction mode |

## Evidence Classes

Create evidence-specific classes by extending ReadWrite:

```python
from python_abraflexi import ReadWrite

class FakturaVydana(ReadWrite):
    """Issued invoice evidence."""
    
    def __init__(self, init=None, options=None):
        if options is None:
            options = {}
        options['evidence'] = 'faktura-vydana'
        super().__init__(init, options)
    
    def pay(self, amount, date):
        """Mark invoice as paid."""
        return self.perform_action('zauctovat', {
            'castka': amount,
            'datum': date
        })

# Usage
invoice = FakturaVydana('code:TEST001', {
    'url': 'https://demo.flexibee.eu',
    'company': 'demo',
    'user': 'winstrom',
    'password': 'winstrom'
})
invoice.pay(1000, '2026-01-25')
```

## Examples

See the `examples/` directory for more usage examples:

- `test_connection.py` - Test connection to AbraFlexi
- `create_invoice.py` - Create new invoice
- `batch_operations.py` - Batch insert/update operations
- `dry_run.py` - Test changes without saving

## Data Types

The library automatically converts between AbraFlexi and Python types:

| AbraFlexi Type | Python Type | Example |
|----------------|-------------|---------|
| string | str | "Text" |
| integer | int | 123 |
| numeric | float | 12.5 |
| date | datetime.date | date(2026, 1, 25) |
| datetime | datetime.datetime | datetime(2026, 1, 25, 14, 30) |
| logic | bool | True/False |
| relation | int/str | 123 or "code:ABC" |

## Error Handling

```python
from python_abraflexi import ReadWrite, NotFoundException, ValidationException

try:
    invoice = ReadWrite(99999, {
        'url': 'https://demo.flexibee.eu',
        'company': 'demo',
        'user': 'winstrom',
        'password': 'winstrom',
        'evidence': 'faktura-vydana'
    })
except NotFoundException:
    print("Invoice not found")
except ValidationException as e:
    print(f"Validation errors: {e.errors}")
```

## Development

### Setup Development Environment

```bash
git clone https://github.com/VitexSoftware/python-abraflexi.git
cd python-abraflexi
python3 -m venv venv
source venv/bin/activate
pip install -e ".[dev]"
```

### Running Tests

```bash
pytest
```

### Code Formatting

```bash
black python_abraflexi/
```

### Building Debian Package

```bash
dpkg-buildpackage -us -uc
```

## Acknowledgments

This library is a Python port of the PHP AbraFlexi library originally created by Spoje.Net.

Special thanks to:
- [Spoje.Net](http://www.spoje.net) for the original PHP implementation
- [ABRA Flexi s.r.o.](https://www.abraflexi.eu/) for their API support

## License

MIT License - see LICENSE file for details

## Links

- **Original PHP Library**: https://github.com/Spoje-NET/php-abraflexi
- **AbraFlexi API Documentation**: https://www.abraflexi.eu/api/dokumentace/
- **AbraFlexi Demo**: https://demo.flexibee.eu

## Author

**Vítězslav Dvořák**
- Email: info@vitexsoftware.cz
- GitHub: [@VitexSoftware](https://github.com/VitexSoftware)
