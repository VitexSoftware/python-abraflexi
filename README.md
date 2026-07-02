# Python AbraFlexi

![python-abraflexi logo](python-abraflexi.svg)

![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

Python library for easy interaction with the Czech economic system AbraFlexi (FlexiBee).

This is a Python port of the [PHP AbraFlexi library](https://github.com/Spoje-NET/php-abraflexi), providing a complete REST API client with an object-oriented interface for all AbraFlexi operations.

## Features

- **Object-Oriented Interface**: Clean, Pythonic API design (`ReadOnly` / `ReadWrite`)
- **Multiple Authentication Methods**: HTTP Basic, JSON login session (`login`/`logout`/`keep_alive`)
- **Type Conversion**: Automatic conversion between AbraFlexi and Python types
- **Pagination & Sorting**: `set_limit`/`set_start`/`iterate_all`/`set_order`
- **Filtering & Detail Levels**: `filter`, `detail=`, `relations=`, `includes=`
- **Transaction Support**: Atomic operations with dry-run mode
- **Batch Operations**: Bulk insert/update, plus filter-scoped mass updates/actions
- **Actions & Locking**: `lock`/`unlock`/`lock_for_ucetni`/`storno`, custom business actions
- **Attachments**: Upload, list, download, thumbnail and delete
- **Changes API**: Company-wide change tracking for incremental sync
- **Reports & QR codes**: PDF/XLSX export, payment QR codes, saved user queries
- **Ready-made evidence classes**: `FakturaVydana` (issued invoices) and `Adresar` (address book),
  built from reusable mixins (`python_abraflexi.mixins`) you can combine for your own evidences
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
sudo apt install python3-abraflexi          # the library
sudo apt install python3-abraflexi-doc      # README/examples
sudo apt install python3-abraflexi-doc-en   # full Sphinx HTML documentation
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

Two ready-made evidence classes are included, built on top of `ReadWrite` and
the reusable mixins in `python_abraflexi.mixins`:

```python
from python_abraflexi import FakturaVydana, Adresar

options = {
    'url': 'https://demo.flexibee.eu',
    'company': 'demo',
    'user': 'winstrom',
    'password': 'winstrom',
}

invoice = FakturaVydana('code:TEST001', options)
invoice.get_labels()                      # LabelsMixin
invoice.lock()                            # locking action
invoice.get_qr_code_base64()              # payment QR code
invoice.export_report(report_name='dodaciList')  # PDF export

customer = Adresar(123, options)
customer.get_notification_email_address()  # contact-fallback email lookup
```

Build your own evidence class the same way, combining `ReadWrite` with just
the mixins you need:

```python
from python_abraflexi import ReadWrite
from python_abraflexi.mixins import LabelsMixin, SumMixin, LockMixin

class FakturaPrijata(LabelsMixin, SumMixin, LockMixin, ReadWrite):
    """Received invoice evidence."""

    def __init__(self, init=None, options=None):
        if options is None:
            options = {}
        options['evidence'] = 'faktura-prijata'
        super().__init__(init, options)

    def pay(self, amount, date):
        """Mark invoice as paid via a custom business action."""
        return self.perform_action('zauctovat', {
            'castka': amount,
            'datum': date
        })

invoice = FakturaPrijata('code:TEST001', options)
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
| relation | `Relation` object | `Relation("code:ABC")`, exposes `.id`/`.code`/`.ext`/`.ean`/`.plu`/`.vat_id`/`.ico`/`.iban`/`.key`/`.hybrid` |

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

## Documentation

Full bilingual (English + Czech) documentation is under [`docs/`](docs/),
built with Sphinx (covers authentication, CRUD, filtering, pagination,
batch operations, attachments, the Changes API, reports, evidence classes
and mixins, error handling, and an autodoc API reference):

```bash
pip install sphinx sphinx-shibuya   # or: apt install python3-sphinx python3-shibuya-sphinx-theme
sphinx-build -b html docs docs/_build
```

Or install the pre-built package: `sudo apt install python3-abraflexi-doc-en`.

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
- **AbraFlexi REST API Reference** (standalone, bilingual): https://github.com/VitexSoftware/abraflexi-api-doc
- **Official AbraFlexi API Documentation**: https://podpora.flexibee.eu/cs/collections/2592813-dokumentace-rest-api
- **AbraFlexi Demo**: https://demo.flexibee.eu

## Author

**Vítězslav Dvořák**
- Email: info@vitexsoftware.cz
- GitHub: [@VitexSoftware](https://github.com/VitexSoftware)
