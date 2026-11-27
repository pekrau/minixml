"Minimalist package for reading, writing, creating and editing an XML element tree."

__version__ = "0.7.1"

__all__ = ["Element", "parse", "read", "unparse", "write"]

from .element import *
from .io import *
