"""Class to represent an XML element.

An instance of Element has a tag, attributes, children and possibly a
parent. An instance can be part of at most one element tree. All
operations should be performed using the methods, which will maintain
the integrity of the references between instances.
"""

__all__ = ["Element"]

import copy
from xml.sax.saxutils import quoteattr


class Element:
    "XML element having a tag, attributes, parent (if any) and children (if any)."

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
        result = []
        result.append(f"<{self.tag}")
        for name, value in self._attributes.items():
            result.append(f" {name}={quoteattr(value)}")
        if len(self):
            result.append(">")
        else:
            result.append("/>")
        return " ".join(result)

    def __getitem__(self, key: [int, str]):
        """If 'key' is int, get the key'th child.
        If 'key' is str, get the value of the attribute.
        """
        if isinstance(key, int):
            try:
                return self._children[key]
            except IndexError:
                raise IndexError(f"no child '{key}' in element {self}")
        try:
            return self._attributes[key]
        except KeyError:
            raise KeyError(f"no attribute '{key}' in element {self}")

    def __setitem__(self, key: [int, str], value):
        """If 'key' is int, set the key'th child. Convert value to str if not Element.
        If 'key' is str, set the value of the attribute.
        """
        if isinstance(key, int):
            try:
                self._children[key] = value if isinstance(value, Element) else str(value)
            except IndexError:
                raise IndexError(f"cannot set child '{key}' in element {self}")
        else:
            self._attributes[key] = value

    def __delitem__(self, key: [int, str]):
        """If 'key' is int, delete the key'th child.
        If 'key' is str, delete the attribute.
        """
        if isinstance(key, int):
            try:
                del self._children[key]
            except IndexError:
                raise IndexError(f"cannot delete child '{key}' in element {self}")
        else:
            try:
                del self._attributes[key]
            except KeyError:
                raise KeyError(f"no attribute '{key}' in element {self}")

    def __contains__(self, key: [str, Element]):
        """If 'key' is str, does this element have the given attribute?
        If 'key' is an Element instance, is it among the children?
        """
        if isinstance(key, Element):
            return key in self._children
        else:
            return key in self._attributes

    def __iter__(self):
        "Iterate over the children of this element."
        yield from self._children

    def __len__(self):
        "Return the number of children of this element."
        return len(self._children)

    def __eq__(self, other):
        "Are this element and the other equal, recursively? Ignores the parent."
        return not self.diff(other)

    def __iadd__(self, other: [str, Element]):
        "Append the other element to the end of the list of children of this element."
        self.append(other)
        return self

    @property
    def tag(self) -> str:
        "Return the tag of this element; read-only."
        return self._tag

    @property
    def parent(self) -> [None, Element]:
        "Return the parent, if any, of this element; read-only."
        return self._parent

    @property
    def attributes(self) -> dict:
        """Return the dictionary of the attributes; read only.
        This is a shallow copy of the dictionary in the instance. Changing
        it will therefore not affect the attributes in the instance.
        """
        return self._attributes.copy()

    @property
    def children(self) -> list:
        """Return the list of children; read only.
        This is a shallow copy of the list in the instance. Changing it
        will therefore not affect the list of children in the instance.
        """
        return list(self._children)

    @property
    def text(self) -> str:
        """Return the text content of this element.
        All children that are non-blank texts are concatenated.
        """
        result = []
        for child in self:
            if isinstance(child, str) and child.strip():
                result.append(child)
        return "".join(result)

    @property
    def root(self) -> Element:
        "Return the root element of this element. May be self."
        result = self
        while result._parent is not None:
            result = result._parent
        return result

    @property
    def depth(self) -> int:
        "Depth of hierarchy for this element; number of parent steps to root."
        result = 0
        elem = self
        while elem._parent is not None:
            result += 1
            elem = elem._parent
        return result

    def get(self, key: str, default=None):
        "Get the value of the 'key' attribute, or return the default if not present."
        return self._attributes.get(key, default)

    def set(self, key: str, value) -> None:
        "Set the value of the attribute in this element."
        self._attributes[key] = value

    def index(self, other: [str, Element]) -> int:
        """Return the slot number for 'other' among the children of this element.
        Checks for element equality, not identity.
        Raise IndexError if not present.
        """
        try:
            return self._children.index(other)
        except ValueError:
            raise ValueError(f"no element '{other}' among children")

    def append(self, other: [str, Element]) -> None:
        "Append the other element to the end of the list of children of this element."
        if isinstance(other, Element):
            if other.parent:
                raise ValueError(f"element '{other}' must have no parent")
            if other is self:
                raise ValueError(f"cannot append element '{other}' to itself")
        self._children.append(other)
        if isinstance(other, Element):
            other._parent = self

    def insert(self, i: int, other: [str, Element]) -> None:
        "Insert 'other' at position 'i' in the list of children of this element."
        if isinstance(other, Element):
            if other.parent:
                raise ValueError(f"element '{other}' must have no parent")
            if other is self:
                raise ValueError(f"cannot insert element '{other}' into itself")
        self._children.insert(i, other)
        if isinstance(other, Element):
            other._parent = self

    def replace(self, i: int, other: [str, Element]) -> [str, Element]:
        """Replace the element at position 'i' in the list of children of
        this element with 'other'. The replaced element is returned.
        """
        if isinstance(other, Element):
            if other.parent:
                raise ValueError(f"element '{other}' must have no parent")
            if other is self:
                raise ValueError(f"cannot replace element '{other}' into itself")
        result = self._children[i]
        if isinstance(result, Element):
            result._parent = None
        self._children[i] = other
        if isinstance(other, Element):
            other._parent = self
        return result

    def pop(self, i: [int, None]=None) -> [str, Element]:
        "Remove the element at position i (last if None) and return it."
        try:
            if i is None:
                result = self._children.pop()
            else:
                result = self._children.pop(i)
        except IndexError:
            raise IndexError(f"no child '{i}' to pop from this element")
        result._parent = None
        return result

    def free(self) -> Element:
        "Remove this element from its parent, if any. Return itself."
        if self._parent is not None:
            self._parent._children.remove(self)
            self._parent = None
        return self

    def create(self, tag: str, **attributes) -> Element:
        """Create an element with the given tag and attributes,
        and append to the children of this element.
        Return the created element.
        """
        # Ensure that the same class is used throughout.
        elem = self.__class__(tag, **attributes)
        self.append(elem)
        return elem

    def copy(self) -> Element:
        """Make a copy of this element and its children (i.e. deepcopy).
        The returned copy element has no parent.
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
        """Walk over this element and all its Element children recursively,
        yielding those elements that match the given test function.
        If no test function given, yield all.
        NOTE: The test function must handle both Element instances and strings.
        """
        if test is not None and not callable(test):
            raise ValueError("'test' for method 'walk' must be a callable or None")
        if test is None or test(self):
            yield self
        for child in self:
            if isinstance(child, Element):
                yield from child.walk(test=test)
            elif test is None or test(child):
                yield child

    def diff(self, other: Element):
        """Return the first difference between this element and the other, recursively.
        Ignores the parents of this element and the other.
        Return a tuple describing the difference, or None.
        """
        if not isinstance(other, self.__class__):
            return ("instance", self, other)
        if self.tag != other.tag:
            return ("tag", self, other)
        if self._attributes != other.attributes:
            return ("attributes", self, other)
        if len(self) != len(other):
            return ("len", self, other)
        for child1, child2 in zip(self._children, other.children):
            if isinstance(child1, Element):
                if result := child1.diff(child2):
                    return result
            elif child1 != child2:
                return ("diff", child1, child2)
        return None
