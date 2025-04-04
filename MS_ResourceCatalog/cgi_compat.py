"""
Compatibility module to provide the functionality of the removed cgi module for CherryPy.
This module is needed because CherryPy 18.8.0 still imports from the cgi module,
which was removed in Python 3.13.
"""

__all__ = ['parse_header']

def parse_header(line):
    """Parse a Content-type like header.
    
    This is a replacement for the removed cgi.parse_header function.
    
    Return the main content-type and a dictionary of parameters.
    """
    if not line:
        return '', {}
        
    parts = line.split(';')
    key = parts[0].strip()
    pdict = {}
    
    for p in parts[1:]:
        if '=' not in p:
            continue
        name, value = p.split('=', 1)
        name = name.strip()
        value = value.strip()
        
        if len(value) >= 2 and value[0] == value[-1] == '"':
            value = value[1:-1]
            value = value.replace('\\\\', '\\').replace('\\"', '"')
        
        pdict[name] = value
    
    return key, pdict 