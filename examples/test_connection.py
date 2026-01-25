#!/usr/bin/env python3
"""
Test connection to AbraFlexi server.

This example demonstrates how to test connectivity to an AbraFlexi server.
"""

import sys
import os

# Add parent directory to path for local development
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from python_abraflexi import ReadOnly


def test_connection():
    """Test connection to AbraFlexi demo server."""
    
    print("Testing connection to AbraFlexi...")
    
    try:
        # Connect to demo server
        test = ReadOnly(None, {
            'url': 'https://demo.flexibee.eu',
            'company': 'demo',
            'user': 'winstrom',
            'password': 'winstrom',
            'evidence': 'c'  # Company evidence
        })
        
        # Get company info
        result = test.perform_request()
        
        if result:
            print("✓ Connection successful!")
            print(f"  Server: {test.url}")
            print(f"  Company: {test.company}")
            return True
        else:
            print("✗ Connection failed - no data returned")
            return False
            
    except Exception as e:
        print(f"✗ Connection failed: {e}")
        return False


if __name__ == "__main__":
    success = test_connection()
    sys.exit(0 if success else 1)
