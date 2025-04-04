"""
Monkey patching module to make CherryPy work with Python 3.13+
This patches the CherryPy library to use our custom implementation
instead of the removed cgi module.
"""
import sys
import os
import importlib.util
import importlib.abc
import importlib.machinery
import types

# Ensure we can import cgi_compat from the current directory
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

# Import our compatibility module
import cgi_compat

class CGILoader(importlib.abc.Loader):
    """Custom loader for our fake cgi module."""
    
    def __init__(self, module):
        """Initialize with the pre-created module."""
        self.module = module
        
    def create_module(self, spec):
        """Return the pre-created module."""
        return self.module
        
    def exec_module(self, module):
        """Nothing to execute."""
        pass

class CGIImportFinder(importlib.abc.MetaPathFinder):
    """Import finder that provides a fake cgi module."""
    
    def find_spec(self, fullname, path, target=None):
        """Find the module spec for the given module name."""
        if fullname == 'cgi':
            # Create a new module
            module = types.ModuleType('cgi')
            # Add the parse_header function to it
            module.parse_header = cgi_compat.parse_header
            
            # Create a spec with our custom loader
            loader = CGILoader(module)
            spec = importlib.machinery.ModuleSpec(name='cgi', loader=loader)
            
            return spec
        return None

def apply_patches():
    """Apply all monkey patches to make the application compatible with Python 3.13+"""
    if sys.version_info >= (3, 13):
        # Register our import finder
        sys.meta_path.insert(0, CGIImportFinder())
        print("Applied compatibility patches for Python 3.13+")
    else:
        print(f"No patches needed for Python {sys.version}") 