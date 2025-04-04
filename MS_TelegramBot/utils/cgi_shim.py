"""
CGI module shim for Python 3.13+ compatibility

This module provides the necessary functions from the removed cgi module 
that CherryPy depends on in Python 3.13+
"""

import sys
import re
from email.parser import HeaderParser
from urllib.parse import parse_qsl

def _parseparam(s):
    """Duplicate of the _parseparam function from the removed cgi module"""
    while s[:1] == ';':
        s = s[1:]
        end = s.find(';')
        while end > 0 and (s.count('"', 0, end) - s.count('\\"', 0, end)) % 2:
            end = s.find(';', end + 1)
        if end < 0:
            end = len(s)
        f = s[:end]
        yield f.strip()
        s = s[end:]

def parse_header(line):
    """Parse a Content-type like header.

    Return the main content-type and a dictionary of parameters.
    """
    parts = _parseparam(';' + line)
    key = next(parts)
    pdict = {}
    for p in parts:
        i = p.find('=')
        if i >= 0:
            name = p[:i].strip().lower()
            value = p[i+1:].strip()
            if len(value) >= 2 and value[0] == value[-1] == '"':
                value = value[1:-1]
                value = value.replace('\\\\', '\\').replace('\\"', '"')
            pdict[name] = value
    return key, pdict

def apply_patch():
    """Apply the patch to make CherryPy work with Python 3.13+"""
    if sys.version_info >= (3, 13):
        try:
            # Verify that the cgi module is missing
            import cgi
            # If we get here, the cgi module exists, no patching needed
            return False
        except ImportError:
            # Create a fake cgi module with the required functions
            import types
            cgi_module = types.ModuleType('cgi')
            cgi_module.parse_header = parse_header
            
            # Add the module to sys.modules
            sys.modules['cgi'] = cgi_module
            return True
    return False 