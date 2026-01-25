"""
Tests for ReadOnly class.
"""

import pytest
from python_abraflexi import ReadOnly
from python_abraflexi.exceptions import (
    AbraFlexiException,
    ConnectionException,
    NotFoundException,
)


class TestReadOnly:
    """Test ReadOnly class."""

    def test_init_without_params(self):
        """Test initialization without parameters."""
        ro = ReadOnly()
        assert ro.evidence is None
        assert ro.format == "json"
        assert ro.timeout == 300

    def test_init_with_options(self):
        """Test initialization with options."""
        ro = ReadOnly(None, {
            'url': 'https://demo.flexibee.eu',
            'company': 'demo',
            'user': 'winstrom',
            'password': 'winstrom',
            'evidence': 'faktura-vydana'
        })
        
        assert ro.url == 'https://demo.flexibee.eu'
        assert ro.company == 'demo'
        assert ro.user == 'winstrom'
        assert ro.evidence == 'faktura-vydana'

    def test_set_evidence(self):
        """Test setting evidence."""
        ro = ReadOnly()
        result = ro.set_evidence('faktura-vydana')
        assert result is True
        assert ro.evidence == 'faktura-vydana'

    def test_set_company(self):
        """Test setting company."""
        ro = ReadOnly()
        ro.set_company('test_company')
        assert ro.company == 'test_company'

    def test_get_evidence_url(self):
        """Test getting evidence URL."""
        ro = ReadOnly(None, {
            'url': 'https://demo.flexibee.eu',
            'company': 'demo',
            'evidence': 'faktura-vydana'
        })
        
        url = ro.get_evidence_url()
        assert url == 'https://demo.flexibee.eu/c/demo/faktura-vydana'

    def test_set_prefix(self):
        """Test setting URL prefix."""
        ro = ReadOnly()
        ro.set_prefix('c')
        assert ro.prefix == '/c/'
        
        ro.set_prefix('admin')
        assert ro.prefix == '/admin/'

    def test_set_format(self):
        """Test setting format."""
        ro = ReadOnly()
        result = ro.set_format('xml')
        assert result is True
        assert ro.format == 'xml'

    def test_data_operations(self):
        """Test data get/set operations."""
        ro = ReadOnly()
        
        ro.set_data_value('kod', 'TEST001')
        assert ro.get_data_value('kod') == 'TEST001'
        
        ro.set_data_value('nazev', 'Test Name')
        data = ro.get_data()
        assert data['kod'] == 'TEST001'
        assert data['nazev'] == 'Test Name'

    def test_take_data(self):
        """Test taking data."""
        ro = ReadOnly()
        
        test_data = {
            'id': 123,
            'kod': 'TEST001',
            'nazev': 'Test'
        }
        
        ro.take_data(test_data)
        assert ro.get_data() == test_data
        assert ro.my_key == 123

    def test_offline_mode(self):
        """Test offline mode."""
        ro = ReadOnly(None, {'offline': True})
        assert ro.offline is True
        
        result = ro.perform_request()
        assert result is False

    def test_str_representation(self):
        """Test string representation."""
        ro = ReadOnly()
        ro.my_key = 'code:TEST001'
        assert str(ro) == 'code:TEST001'
        
    def test_repr_representation(self):
        """Test repr representation."""
        ro = ReadOnly()
        ro.evidence = 'faktura-vydana'
        ro.my_key = 123
        assert 'ReadOnly' in repr(ro)
        assert 'faktura-vydana' in repr(ro)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
