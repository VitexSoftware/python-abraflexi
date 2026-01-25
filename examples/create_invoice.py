#!/usr/bin/env python3
"""
Create new invoice in AbraFlexi.

This example demonstrates how to create a new invoice.
"""

import sys
import os
from datetime import date

# Add parent directory to path for local development
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from python_abraflexi import ReadWrite


def create_invoice():
    """Create new invoice in AbraFlexi."""
    
    print("Creating new invoice...")
    
    try:
        # Create invoice object
        invoice = ReadWrite(None, {
            'url': 'https://demo.flexibee.eu',
            'company': 'demo',
            'user': 'winstrom',
            'password': 'winstrom',
            'evidence': 'faktura-vydana'
        })
        
        # Set invoice data
        invoice.set_data_value('kod', f'PY-TEST-{date.today().isoformat()}')
        invoice.set_data_value('nazev', 'Test Invoice from Python')
        invoice.set_data_value('firma', 'code:ABCFIRM1')
        invoice.set_data_value('datVyst', date.today().isoformat())
        invoice.set_data_value('typDokl', 'code:FAKTURA')
        
        # Insert to AbraFlexi
        result = invoice.insert_to_abraflexi()
        
        if result and invoice.last_inserted_id:
            print(f"✓ Invoice created successfully!")
            print(f"  ID: {invoice.last_inserted_id}")
            print(f"  Code: {invoice.get_data_value('kod')}")
            return True
        else:
            print("✗ Failed to create invoice")
            if invoice.errors:
                print(f"  Errors: {invoice.errors}")
            return False
            
    except Exception as e:
        print(f"✗ Error creating invoice: {e}")
        return False


if __name__ == "__main__":
    success = create_invoice()
    sys.exit(0 if success else 1)
