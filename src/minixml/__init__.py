"Minimalist package for reading, writing, creating and editing an XML element tree."

__version__ = "0.6.5"

__all__ = ["Element", "parse", "read", "unparse", "write"]

from .element import *
from .io import *
