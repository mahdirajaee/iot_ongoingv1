"""
CherryPy compatibility module for Python 3.13.1

This module provides compatibility for functions removed from the standard library in Python 3.13
"""
import sys
import re
import email.parser

# Monkey patch for parse_header from cgi module
def parse_header(line):
    """Parse a Content-type like header.
    
    Return the main content-type and a dictionary of parameters.
    This replaces the removed cgi.parse_header function in Python 3.13
    """
    if not line:
        return '', {}
        
    # Use email.parser to parse the header
    parser = email.parser.HeaderParser()
    header = parser.parsestr(f'Content-Type: {line}')
    
    # Extract main value and parameters
    main_value = header.get_content_type()
    params = {}
    
    # Extract parameters from the header
    for key, value in header.get_params():
        if key != 'Content-Type':  # Skip the main content type
            params[key] = value
            
    return main_value, params

# Apply monkey patch if in Python 3.13+
if sys.version_info >= (3, 13):
    import builtins
    
    # Create a fake cgi module
    class FakeCGIModule:
        def __getattr__(self, name):
            if name == 'parse_header':
                return parse_header
            raise AttributeError(f"module 'cgi' has no attribute '{name}'")
    
    # Add the fake module to sys.modules
    sys.modules['cgi'] = FakeCGIModule() 