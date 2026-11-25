"Minimalist module for reading, writing, creating and editing an XML element tree."

__version__ = "0.5.0"

__all__ = ["Element", "read", "parse", "__version__"]

import copy
import io
import xml.sax
from xml.sax.saxutils import quoteattr, escape, unescape


class Element:
    "XML element having a tag, attributes, parent (if any) and children (if any)."

    # If truthy value, output if the element is root (i.e has no parent). For 'repr()'.
    REPR_DECL = '<?xml version="1.0" encoding="utf-8"?>'

    # Indentation to use for 'repr()'.
    REPR_INDENT = 2

    def __init__(self, tag: str, *children, **attributes):
        "The instance is initialized as a root element (i.e. it has no parent)."
        if not tag:
            raise ValueError("'tag' may not be empty")
        self._tag = tag
        self._parent = None
        self._children = []
        for child in children:
            self.append(child)
        self._attributes = {}
        for name, value in attributes.items():
            self[name] = value

    def __str__(self):
        "Return the string representation of the element's starting tag."
        outfile = io.StringIO()
        outfile.write(f"<{self.tag}")
        for name, value in self._attributes.items():
            outfile.write(f" {name}={quoteattr(value)}")
        if len(self):
            outfile.write(">")
        else:
            outfile.write("/>")
        return outfile.getvalue()

    def __repr__(self):
        """Return the XML code for the element and all its children.
        The class variable REPR_INDENT determines the indentation of the XML code.
        The class variable REPR_DECL is output first if it is truthy
        and this element is the root (i.e. it has no parent).
        """
        outfile = io.StringIO()
        self.write(
            outfile,
            indent=self.REPR_INDENT,
            decl=self.depth == 0 and self.REPR_DECL,
        )
        return outfile.getvalue()

    def __getitem__(self, key):
        "Get the value of the attribute in this element."
        try:
            return self._attributes[key]
        except KeyError:
            raise KeyError(f"no such attribute '{key}' in element {self}")

    def __setitem__(self, key, value):
        "Set the value of the attribute in this element."
        if not isinstance(value, str):
            value = str(value)
        self._attributes[key] = value

    def __delitem__(self, key):
        "Delete the attribute in this element."
        try:
            del self._attributes[key]
        except KeyError:
            raise KeyError(f"no such attribute '{key}' in element {self}")

    def __contains__(self, key):
        "Does this element have the given attribute?"
        return key in self._attributes

    def __iter__(self):
        "Iterate over the children of this element."
        yield from self._children

    def __len__(self):
        "Return the number of children of this element."
        return len(self._children)

    def __eq__(self, element):
        "Are the element and its children equal? Ignores the parent."
        if not isinstance(element, Element):
            return False
        if self.tag != element.tag:
            return False
        if self._attributes != element._attributes:
            return False
        if len(self) != len(element):
            return False
        for child1, child2 in zip(self._children, element._children):
            if child1 != child2:
                return False
        return True

    def __iadd__(self, element):
        "Append the element to the end of the list of children of this element."
        self.append(element)
        return self

    @property
    def tag(self):
        "Return the element tag; read-only."
        return self._tag

    @property
    def parent(self):
        "Return the parent element, if any; read-only."
        return self._parent

    @property
    def attributes(self):
        """Return the dictionary of the attributes; read only.
        This is a shallow copy of the dictionary in the instance. Changing
        it will therefore not affect the attributes in the instance.
        """
        return self._attributes.copy()

    @property
    def children(self):
        """Return the list of children; read only.
        This is a shallow copy of the list in the instance. Changing it
        will therefore not affect the list of children in the instance.
        """
        return list(self._children)

    @property
    def text(self):
        """Return the text content of this element.
        All children that are non-blank texts are concatenated.
        """
        result = []
        for child in self:
            if isinstance(child, str) and child.strip():
                result.append(child)
        return "".join(result)

    @property
    def root(self):
        "Return the root element of this element."
        result = self
        while result._parent is not None:
            result = result._parent
        return result

    @property
    def depth(self):
        "Depth of hierarchy for this element; number of parent steps to root."
        result = 0
        elem = self
        while elem._parent is not None:
            result += 1
            elem = elem._parent
        return result

    def get(self, key, default=None):
        "Return the value of the given attribute in this element, or the default."
        try:
            return self[key]
        except KeyError:
            return default

    def set(self, key, value):
        "Set the value of the attribute in this element."
        self[key] = value

    def insert(self, i, elem):
        "Insert the element at position i in the list of children of this element."
        assert isinstance(elem, (Element, str)), elem
        assert self is not elem
        if isinstance(elem, Element):
            if elem.parent:
                raise ValueError(
                    f"element {elem} has not been freed from its parent {elem.parent}"
                )
        self._children.insert(i, elem)
        if isinstance(elem, Element):
            elem._parent = self

    def append(self, elem):
        "Append the element to the end of the list of children of this element."
        assert isinstance(elem, (Element, str)), elem
        assert self is not elem
        if isinstance(elem, Element):
            if elem.parent:
                raise ValueError(
                    f"element {elem} has not been freed from its parent {elem.parent}"
                )
        self._children.append(elem)
        if isinstance(elem, Element):
            elem._parent = self

    def free(self):
        "Remove this element from its parent, if any. Return itself."
        if self._parent is not None:
            self._parent._children.remove(self)
            self._parent = None
        return self

    def create(self, tag, **attributes):
        """Create an element with the given tag and attributes,
        and append to the children of this element.
        Return the created element.
        """
        elem = self.__class__(
            tag, **attributes
        )  # Ensure that the same class is used throughout.
        self.append(elem)
        return elem

    def copy(self):
        """Make a copy of this element and its children (i.e. deepcopy).
        The returned new element copy has no parent.
        """
        result = copy.deepcopy(self)
        result._parent = None
        result._set_parent()
        return result

    def _set_parent(self):
        "Set the correct parent for all children recursively."
        for child in self:
            if isinstance(child, Element):
                child._parent = self
                child._set_parent()

    def walk(self, test=None):
        """Walk over this element and all its children recursively,
        yielding those elements that match the given test function.
        If no test function given, yield all.
        NOTE: The test function must handle both Element instances and strings.
        """
        if test is not None and not callable(test):
            raise TypeError("'test' for method 'walk' must be a callable or None")
        assert test is None or callable(test)
        if test is None or test(self):
            yield self
        for child in self:
            if isinstance(child, Element):
                yield from child.walk(test=test)
            elif test is None or test(child):
                yield child

    def diff(self, element):
        "Return the first difference between this element and the element, recursively."
        if not isinstance(element, self.__class__):
            return ("instance", self, element)
        if self.tag != element.tag:
            return ("tag", self, element)
        if self._attributes != element._attributes:
            return ("attributes", self, element)
        if len(self) != len(element):
            return ("len", self, element)
        for child1, child2 in zip(self._children, element._children):
            if isinstance(child1, Element):
                if result := child1.diff(child2):
                    return result
            elif child1 != child2:
                return ("diff", child1, child2)

    def output(self, indent=None, decl=True):
        """Return the XML code for the element and its children as a string.
        The 'decl' value is output first if it is truthy and this element
        is the root (i.e. has no parent). The default: 'self.REPR_DECL'
        """
        assert indent is None or (isinstance(indent, int) and indent >= 0)
        outfile = io.StringIO()
        if decl is True:
            decl = self.REPR_DECL
        self.write(outfile, indent=indent, decl=self.depth == 0 and decl)
        return outfile.getvalue()

    def write(self, outfile, indent=None, decl=False):
        """Write the XML of the element and its children into the open file object.
        The 'decl' value is output first if it is a non-empty string.
        """
        assert indent is None or (isinstance(indent, int) and indent >= 0)
        if decl:
            outfile.write(decl + "\n")
        if indent is None:
            padding = ""
        else:
            padding = " " * indent * self.depth
        outfile.write(padding)
        outfile.write(f"<{self.tag}")
        for name, value in self._attributes.items():
            outfile.write(f" {name}={quoteattr(value)}")
        if len(self):
            outfile.write(">")
            newline = False
            for elem in self:
                if isinstance(elem, Element):
                    if indent:
                        outfile.write("\n")
                    elem.write(outfile, indent=indent)
                    newline = True
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
            outfile.write(f"</{self.tag}>")
        else:
            outfile.write("/>")


def parse(content, element_class=Element):
    "Parse the given XML content (string). Return the root XML element."
    try:
        return read(io.StringIO(content), element_class=element_class)
    except ValueError as error:
        raise ValueError(f"{str(error)}: {content}")


def read(filepath_or_stream, element_class=Element):
    """Read and parse the file given by its path, or the open file object.
    Returns the root Element.
    """
    try:
        content_handler = ContentHandler(element__class=element_class)
        xml.sax.parse(filepath_or_stream, content_handler)
    except xml.sax.SAXException as error:
        raise ValueError(f"XML parse error: {error}")
    return content_handler.root


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


def test():
    original = parse("""<?xml version="1.0" encoding="utf-8" ?>
<package xmlns="http://www.idpf.org/2007/opf" xmlns:dc="http://purl.org/dc/elements/1.1/" unique-identifier="db-id" version="3.0">
<metadata>
<dc:title id="t1">Sample .epub Book</dc:title>
<dc:creator id="creator">Thomas Hansen</dc:creator>
<dc:identifier id="db-id">isbn</dc:identifier>
<meta property="dcterms:modified">2014-03-27T09:14:09Z</meta>
<dc:language>en</dc:language>
</metadata>
</package>""")

    root = Element("package", xmlns="http://www.idpf.org/2007/opf", version="3.0")
    root["xmlns:dc"] = "http://purl.org/dc/elements/1.1/"
    root["unique-identifier"] = "db-id"
    metadata = root.create("metadata")
    metadata.create("dc:title", id="t1").append("Sample .epub Book")
    metadata.create("dc:creator", id="creator").append("Thomas Hansen")
    metadata.create("dc:identifier", id="db-id").append("isbn")
    metadata.create("meta", property="dcterms:modified").append("2014-03-27T09:14:09Z")
    metadata.create("dc:language").append("en")

    if diff := original.diff(root):
        print(diff)


if __name__ == "__main__":
    test()
