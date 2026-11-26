# minixml

Minimalist module for reading, writing, creating and editing an XML element tree.

This code has been lovingly hand-crafted. No AI tools were used in its development.

There are no dependencies except for the standard Python library.

# Table of Contents

* [minixml](#minixml)
* [minixml.element](#minixml.element)
  * [Element](#minixml.element.Element)
    * [\_\_init\_\_](#minixml.element.Element.__init__)
    * [\_\_str\_\_](#minixml.element.Element.__str__)
    * [\_\_getitem\_\_](#minixml.element.Element.__getitem__)
    * [\_\_setitem\_\_](#minixml.element.Element.__setitem__)
    * [\_\_delitem\_\_](#minixml.element.Element.__delitem__)
    * [\_\_contains\_\_](#minixml.element.Element.__contains__)
    * [\_\_iter\_\_](#minixml.element.Element.__iter__)
    * [\_\_len\_\_](#minixml.element.Element.__len__)
    * [\_\_eq\_\_](#minixml.element.Element.__eq__)
    * [\_\_iadd\_\_](#minixml.element.Element.__iadd__)
    * [tag](#minixml.element.Element.tag)
    * [parent](#minixml.element.Element.parent)
    * [attributes](#minixml.element.Element.attributes)
    * [children](#minixml.element.Element.children)
    * [text](#minixml.element.Element.text)
    * [root](#minixml.element.Element.root)
    * [depth](#minixml.element.Element.depth)
    * [get](#minixml.element.Element.get)
    * [set](#minixml.element.Element.set)
    * [insert](#minixml.element.Element.insert)
    * [append](#minixml.element.Element.append)
    * [free](#minixml.element.Element.free)
    * [create](#minixml.element.Element.create)
    * [copy](#minixml.element.Element.copy)
    * [walk](#minixml.element.Element.walk)
    * [diff](#minixml.element.Element.diff)
* [minixml.io](#minixml.io)
  * [parse](#minixml.io.parse)
  * [read](#minixml.io.read)
  * [unparse](#minixml.io.unparse)
  * [write](#minixml.io.write)
  * [ContentHandler](#minixml.io.ContentHandler)

<a id="minixml"></a>

# minixml

Minimalist package for reading, writing, creating and editing an XML element tree.

<a id="minixml.element"></a>

# minixml.element

Element class.

<a id="minixml.element.Element"></a>

## Element Objects

```python
class Element()
```

XML element having a tag, attributes, parent (if any) and children (if any).

<a id="minixml.element.Element.__init__"></a>

#### \_\_init\_\_

```python
def __init__(tag: str, *children, **attributes)
```

The instance is initialized as a root element (i.e. it has no parent).

<a id="minixml.element.Element.__str__"></a>

#### \_\_str\_\_

```python
def __str__()
```

Return the string representation of the element's starting tag.

<a id="minixml.element.Element.__getitem__"></a>

#### \_\_getitem\_\_

```python
def __getitem__(key)
```

Get the value of the attribute in this element.

<a id="minixml.element.Element.__setitem__"></a>

#### \_\_setitem\_\_

```python
def __setitem__(key, value)
```

Set the value of the attribute in this element.

<a id="minixml.element.Element.__delitem__"></a>

#### \_\_delitem\_\_

```python
def __delitem__(key)
```

Delete the attribute in this element.

<a id="minixml.element.Element.__contains__"></a>

#### \_\_contains\_\_

```python
def __contains__(key)
```

Does this element have the given attribute?

<a id="minixml.element.Element.__iter__"></a>

#### \_\_iter\_\_

```python
def __iter__()
```

Iterate over the children of this element.

<a id="minixml.element.Element.__len__"></a>

#### \_\_len\_\_

```python
def __len__()
```

Return the number of children of this element.

<a id="minixml.element.Element.__eq__"></a>

#### \_\_eq\_\_

```python
def __eq__(other)
```

Are this element and the other equal, recursively? Ignores the parent.

<a id="minixml.element.Element.__iadd__"></a>

#### \_\_iadd\_\_

```python
def __iadd__(other)
```

Append the other to the end of the list of children of this other.

<a id="minixml.element.Element.tag"></a>

#### tag

```python
@property
def tag()
```

Return the tag of this element; read-only.

<a id="minixml.element.Element.parent"></a>

#### parent

```python
@property
def parent()
```

Return the parent, if any, of this element; read-only.

<a id="minixml.element.Element.attributes"></a>

#### attributes

```python
@property
def attributes()
```

Return the dictionary of the attributes; read only.
This is a shallow copy of the dictionary in the instance. Changing
it will therefore not affect the attributes in the instance.

<a id="minixml.element.Element.children"></a>

#### children

```python
@property
def children()
```

Return the list of children; read only.
This is a shallow copy of the list in the instance. Changing it
will therefore not affect the list of children in the instance.

<a id="minixml.element.Element.text"></a>

#### text

```python
@property
def text()
```

Return the text content of this element.
All children that are non-blank texts are concatenated.

<a id="minixml.element.Element.root"></a>

#### root

```python
@property
def root()
```

Return the root element of this element. May be self.

<a id="minixml.element.Element.depth"></a>

#### depth

```python
@property
def depth()
```

Depth of hierarchy for this element; number of parent steps to root.

<a id="minixml.element.Element.get"></a>

#### get

```python
def get(key, default=None)
```

Return the value of the given attribute in this element, or the default.

<a id="minixml.element.Element.set"></a>

#### set

```python
def set(key, value)
```

Set the value of the attribute in this element.

<a id="minixml.element.Element.insert"></a>

#### insert

```python
def insert(i, other)
```

Insert the element at position i in the list of children of this element.

<a id="minixml.element.Element.append"></a>

#### append

```python
def append(other)
```

Append the element to the end of the list of children of this element.

<a id="minixml.element.Element.free"></a>

#### free

```python
def free()
```

Remove this element from its parent, if any. Return itself.

<a id="minixml.element.Element.create"></a>

#### create

```python
def create(tag, **attributes)
```

Create an element with the given tag and attributes,
and append to the children of this element.
Return the created element.

<a id="minixml.element.Element.copy"></a>

#### copy

```python
def copy()
```

Make a copy of this element and its children (i.e. deepcopy).
The returned copy element has no parent.

<a id="minixml.element.Element.walk"></a>

#### walk

```python
def walk(test=None)
```

Walk over this element and all its Element children recursively,
yielding those elements that match the given test function.
If no test function given, yield all.
NOTE: The test function must handle both Element instances and strings.

<a id="minixml.element.Element.diff"></a>

#### diff

```python
def diff(other)
```

Return the first difference between this element and the other, recursively.
Ignores the parents of this element and the other.
Return a tuple describing the difference, or None.

<a id="minixml.io"></a>

# minixml.io

Parse operation on Element.

<a id="minixml.io.parse"></a>

#### parse

```python
def parse(content, element_class=Element)
```

Parse the given XML content (string). Return the root XML element.

<a id="minixml.io.read"></a>

#### read

```python
def read(filepath_or_stream, element_class=Element)
```

Read and parse the file given by its path, or the open file object.
Return the root Element.

<a id="minixml.io.unparse"></a>

#### unparse

```python
def unparse(element, indent=0, decl='<?xml version="1.0" encoding="utf-8"?>')
```

Return the XML code for the element and its children as a string.
'indent' is the number of blanks to use for each indentation level.
The 'decl' value is output first if it is a non-empty string.

<a id="minixml.io.write"></a>

#### write

```python
def write(outfile,
          element,
          indent=0,
          decl='<?xml version="1.0" encoding="utf-8"?>')
```

Write the XML of the element and its children into the open file object.
The 'decl' value is output first if it is a non-empty string.

<a id="minixml.io.ContentHandler"></a>

## ContentHandler Objects

```python
class ContentHandler(xml.sax.ContentHandler)
```

Parse XML read events into an Element tree.


