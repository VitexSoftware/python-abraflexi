# Conversion Summary: PHP AbraFlexi → Python AbraFlexi

This document summarizes the conversion of the PHP AbraFlexi library to Python.

## Source
- **Repository**: /home/vitex/Projects/SpojeNet/php-abraflexi
- **Language**: PHP 8.1+
- **Package**: spojenet/flexibee (Composer)
- **Version**: 3.6

## Target
- **Repository**: /home/vitex/Projects/VitexSoftware/python-abraflexi
- **Language**: Python 3.8+
- **Package**: python3-vitexsoftware-abraflexi (pip/deb)
- **Version**: 1.0.0

## Conversion Details

### Core Library Components

#### 1. Base Classes
| PHP Class | Python Module | Status |
|-----------|---------------|--------|
| `src/AbraFlexi/RO.php` | `python_abraflexi/read_only.py` | ✅ Converted |
| `src/AbraFlexi/RW.php` | `python_abraflexi/read_write.py` | ✅ Converted |

**Key Changes:**
- PHP cURL → Python requests library
- PHP arrays → Python dicts/lists
- camelCase methods → snake_case (Python convention)
- Native PHP types → Python type hints

#### 2. Supporting Classes
| Component | PHP | Python | Status |
|-----------|-----|--------|--------|
| Exceptions | Various | `exceptions.py` | ✅ Created |
| Relations | Relation class | `relation.py` | ✅ Converted |
| Package Init | autoload | `__init__.py` | ✅ Created |

#### 3. Evidence Classes
Evidence-specific classes (FakturaVydana, FakturaPrijata, etc.) can be created by extending ReadWrite:

```python
class FakturaVydana(ReadWrite):
    def __init__(self, init=None, options=None):
        if options is None:
            options = {}
        options['evidence'] = 'faktura-vydana'
        super().__init__(init, options)
```

### Configuration

#### PHP Configuration
```php
define('ABRAFLEXI_URL', 'https://abraflexi-dev.spoje.net:5434');
define('ABRAFLEXI_LOGIN', 'apiuser');
define('ABRAFLEXI_PASSWORD', 'apipass');
define('ABRAFLEXI_COMPANY', 'test_s_r_o_');
```

#### Python Configuration
```python
import os
os.environ['ABRAFLEXI_URL'] = 'https://abraflexi-dev.spoje.net:5434'
os.environ['ABRAFLEXI_LOGIN'] = 'apiuser'
os.environ['ABRAFLEXI_PASSWORD'] = 'apipass'
os.environ['ABRAFLEXI_COMPANY'] = 'test_s_r_o_'
```

Or via constructor:
```python
obj = ReadWrite(None, {
    'url': 'https://...',
    'user': 'apiuser',
    'password': 'apipass',
    'company': 'test_s_r_o_'
})
```

### API Equivalents

#### Creating New Record

**PHP:**
```php
$invoice = new \AbraFlexi\FakturaVydana(null, [
    'company' => 'demo',
    'url' => 'https://demo.flexibee.eu/'
]);

$invoice->setDataValue('kod', 'TEST001');
$invoice->setDataValue('nazev', 'Test Invoice');
$invoice->insertToAbraFlexi();
```

**Python:**
```python
from python_abraflexi import ReadWrite

invoice = ReadWrite(None, {
    'company': 'demo',
    'url': 'https://demo.flexibee.eu/',
    'evidence': 'faktura-vydana'
})

invoice.set_data_value('kod', 'TEST001')
invoice.set_data_value('nazev', 'Test Invoice')
invoice.insert_to_abraflexi()
```

#### Reading Records

**PHP:**
```php
$invoice = new \AbraFlexi\FakturaVydana('code:TEST001');
$allInvoices = $invoice->getAllFromAbraFlexi();
```

**Python:**
```python
invoice = ReadWrite('code:TEST001', {
    'evidence': 'faktura-vydana'
})
all_invoices = invoice.get_all_from_abraflexi()
```

### Packaging

#### PHP (Composer)
```json
{
  "require": {
    "spojenet/flexibee": "^3.6"
  }
}
```

#### Python (pip)
```bash
pip install python-abraflexi
```

#### Debian Package

**PHP:**
- Package: `php-spojenet-abraflexi`
- Dependencies: php-curl, php-xml, php-vitexsoftware-ease-core

**Python:**
- Package: `python3-vitexsoftware-abraflexi`
- Dependencies: python3-requests, python3-dateutil, python3-urllib3

### Testing

#### PHP (PHPUnit)
```bash
phpunit tests/
```

#### Python (pytest)
```bash
pytest tests/
```

### Directory Structure

```
python-abraflexi/
├── python_abraflexi/          # Main package (was src/AbraFlexi/)
│   ├── __init__.py
│   ├── read_only.py          # RO.php
│   ├── read_write.py         # RW.php
│   ├── exceptions.py         # New
│   └── relation.py           # Relation class
├── examples/                  # Examples/
│   ├── test_connection.py
│   └── create_invoice.py
├── tests/                     # tests/
│   ├── __init__.py
│   └── test_read_only.py
├── debian/                    # debian/
│   ├── control
│   ├── rules
│   ├── changelog
│   ├── copyright
│   └── compat
├── docs/                      # docs/
├── setup.py                   # New (pip packaging)
├── pyproject.toml            # New (modern Python packaging)
├── requirements.txt          # composer.json equivalent
├── MANIFEST.in              # New
├── .gitignore               # Updated for Python
├── LICENSE                   # MIT (same as PHP)
├── README.md                 # Updated for Python
└── WARP.md                   # Agent guidance
```

## Key Differences

### Language Conventions
- **Naming**: camelCase → snake_case for methods
- **Arrays**: PHP arrays → Python dicts/lists
- **Null**: PHP null → Python None
- **Booleans**: PHP true/false → Python True/False

### HTTP Client
- **PHP**: cURL extension
- **Python**: requests library
- Benefits: Simpler API, better session handling, cleaner code

### Authentication
Both support:
- Basic HTTP authentication (username/password)
- Session ID authentication
- Environment variable configuration

### Type System
- **PHP**: Weak typing with type hints (8.1+)
- **Python**: Dynamic typing with type hints (3.8+)
- Both: Automatic conversion of AbraFlexi types to native types

### Exceptions
- **PHP**: Custom exceptions extending \Exception
- **Python**: Custom exceptions extending Exception
- Same hierarchy: AbraFlexiException → specific exceptions

## Testing the Conversion

### Quick Test
```bash
cd /home/vitex/Projects/VitexSoftware/python-abraflexi

# Install in development mode
pip install -e .

# Run tests
pytest tests/ -v

# Test connection example
python3 examples/test_connection.py
```

### Building Debian Package
```bash
cd /home/vitex/Projects/VitexSoftware/python-abraflexi
dpkg-buildpackage -us -uc
```

## Not Yet Implemented

The following features from the PHP library are not yet implemented in this initial Python version:

1. **Evidence Auto-generation**: Tools to auto-generate evidence classes from API
2. **Structure/Actions/Relations Classes**: Static metadata classes
3. **All Evidence Classes**: Only base classes created, specific evidences need to be added
4. **Advanced Features**:
   - Object chaining
   - Some specialized URL parameters
   - PDF/XLS export helpers
5. **Complete Test Suite**: Only basic tests created

These can be added incrementally as needed.

## Next Steps

1. **Generate Evidence Classes**: Create Python equivalents for all AbraFlexi evidences
2. **Add More Examples**: Port more examples from PHP version
3. **Complete Test Suite**: Add integration tests with demo server
4. **Add to PyPI**: Publish package to Python Package Index
5. **Documentation**: Generate API docs with Sphinx
6. **CI/CD**: Set up automated testing and packaging

## Resources

- **Original PHP Library**: https://github.com/Spoje-NET/php-abraflexi
- **Python Version**: ~/Projects/VitexSoftware/python-abraflexi
- **AbraFlexi API Docs**: https://www.abraflexi.eu/api/dokumentace/
- **Demo Server**: https://demo.flexibee.eu

## Author

Conversion performed by AI assistant for Vítězslav Dvořák (info@vitexsoftware.cz)

Date: January 25, 2026
