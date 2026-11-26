"Parse operation on Element."

__all__ = ["parse", "read", "unparse", "write"]


import io
import xml.sax
from xml.sax.saxutils import quoteattr, escape, unescape

from .element import Element


def parse(content, element_class=Element):
    "Parse the given XML content (string). Return the root XML element."
    return read(io.StringIO(content), element_class=element_class)


def read(filepath_or_stream, element_class=Element):
    """Read and parse the file given by its path, or the open file object.
    Return the root Element.
    """
    content_handler = ContentHandler(element_class=element_class)
    try:
        xml.sax.parse(filepath_or_stream, content_handler)
    except xml.sax.SAXException as error:
        raise ValueError(f"XML parse error: {error}")
    return content_handler.root


def unparse(element, indent=0, decl='<?xml version="1.0" encoding="utf-8"?>'):
    """Return the XML code for the element and its children as a string.
    'indent' is the number of blanks to use for each indentation level.
    The 'decl' value is output first if it is a non-empty string.
    """
    assert isinstance(indent, int) and indent >= 0
    outfile = io.StringIO()
    write(outfile, element, indent=indent, decl=decl)
    return outfile.getvalue()


def write(outfile, element, indent=0, decl='<?xml version="1.0" encoding="utf-8"?>'):
    """Write the XML of the element and its children into the open file object.
    The 'decl' value is output first if it is a non-empty string.
    """
    assert isinstance(indent, int) and indent >= 0
    if decl:
        outfile.write(decl + "\n")
    _write(outfile, element, "", indent)


def _write(outfile, element, padding, indent):
    "Recursively write out the element and its children."
    outfile.write(padding)
    outfile.write(f"<{element.tag}")
    for name, value in element.attributes.items():
        outfile.write(f" {name}={quoteattr(value)}")
    if len(element):
        outfile.write(">")
        newline = False
        for elem in element:
            if isinstance(elem, Element):
                if indent:
                    outfile.write("\n")
                newline = True
                _write(outfile, elem, padding + " " * indent, indent)
            elif isinstance(elem, str):
                outfile.write(escape(elem))
                newline = False
            else:
                outfile.write(escape(str(elem)))
                newline = False
        if newline:
            if indent:
                outfile.write("\n")
            outfile.write(padding)
        outfile.write(f"</{element.tag}>")
    else:
        outfile.write("/>")


class ContentHandler(xml.sax.ContentHandler):
    "Parse XML read events into an Element tree."

    def __init__(self, element_class=Element):
        assert issubclass(element_class, Element)
        self.element_class = element_class
        self.stack = []
        self.root = None

    def startElement(self, tag: str, attributes):
        elem = self.element_class(tag, **dict(attributes))
        if self.stack:
            self.stack[-1]._children.append(elem)
            elem._parent = self.stack[-1]
        else:
            self.root = elem
        self.stack.append(elem)

    def endElement(self, tag: str):
        self.stack.pop()

    def characters(self, content: str):
        if content := content.strip():
            self.stack[-1]._children.append(unescape(content))
