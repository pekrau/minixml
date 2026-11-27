"Test properties and actions on Element instances."

import pytest
from minixml import Element


def test_create_basic():
    "Basic element instance creation."
    a = Element("a")
    assert isinstance(a, Element)
    assert a.tag == "a"
    assert len(a) == 0
    assert a.parent == None
    assert a.root == a
    assert a.children == []
    assert a.attributes == {}


def test_create_attribute():
    "Element instance creation with attribute."
    b = Element("b", style="c")
    assert b.attributes == {"style": "c"}
    assert "style" in b
    assert b["style"] == "c"
    del b["style"]
    assert "style" not in b

def test_element_tree():
    "Element children creation and manipulation."
    a = Element("a")
    b = a.create("b")
    assert b.parent is a
    c = a.create("c")
    assert c.parent is a
    d = c.create("d")
    assert d.parent is c
    assert len(a) == 2
    assert a.children == [b, c]
    with pytest.raises(ValueError):
        a.append(d)
    e = Element("e")
    a += e
    assert len(a) == 3
    assert a.children == [b, c, e]
    assert c.parent is not None
    c.free()
    assert c.parent is None
    assert len(a) == 2
    assert a.children == [b, e]
    a += c
    assert len(a) == 3
    assert a.children == [b, e, c]
    x = a.pop(2)
    assert x is c
    assert a.children == [b, e]
    d = Element("d")
    y = a.replace(1, d)
    assert y is e
    assert y.parent is None
    assert a.children == [b, d]
    assert a.index(b) == 0
    a[0] = y
    assert b not in a
    assert y in a
    with pytest.raises(ValueError):
        i = a.index(b)
    assert a[-1] is d

def test_tree_copy():
    "A copy creates new instances all the way down."
    x = Element("x")
    a = x.create("a")
    b = a.create("b", property="heavy")
    c = a.create("c", style="blue")
    assert len(a) == 2
    assert a.children == [b, c]
    ac = a.copy()
    assert ac.parent is None
    assert len(ac) == 2
    assert a == ac
    ac.children[1]["style"] = "red"
    assert a != ac
    ac.children[1]["style"] = "blue"
    assert a == ac
    ac.create("d")
    assert a != ac
    assert a.diff(ac) == ("len", a, ac)

def test_tree_walk():
    "Return all elements in the tree, or those that match a test function."
    a = Element("a")
    b = a.create("b", property="heavy")
    c = a.create("c", style="blue")
    c.append("Some string")
    assert list(a.walk()) == [a, b, c, "Some string"]
    def test(e):
        if isinstance(e, Element):
            return e.get("property") == "heavy"
    assert list(a.walk(test)) == [b]
