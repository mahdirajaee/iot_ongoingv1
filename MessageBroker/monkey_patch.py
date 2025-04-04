"""
Monkey patch for Python 3.13 compatibility.
This patch replaces references to the removed cgi module in CherryPy.
"""

import sys
import importlib.abc
import importlib.machinery
import types

class CGIFinder(importlib.abc.MetaPathFinder):
    def find_spec(self, fullname, path, target=None):
        if fullname == 'cgi':
            loader = CGILoader()
            return importlib.machinery.ModuleSpec(fullname, loader)
        return None

class CGILoader(importlib.abc.Loader):
    def create_module(self, spec):
        module = types.ModuleType('cgi')
        # Import our compatibility module using absolute import
        import cgi_compat
        # Add the parse_header function to the module
        module.parse_header = cgi_compat.parse_header
        return module

    def exec_module(self, module):
        pass

def apply_patch():
    """Apply the monkey patch if running on Python 3.13+"""
    if sys.version_info >= (3, 13):
        sys.meta_path.insert(0, CGIFinder())
        print("Applied cgi module compatibility patch for Python 3.13+")