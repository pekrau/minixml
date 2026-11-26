"Test parse/unparse operations."

import io
import pytest
from minixml import parse, read, unparse, write, Element


def test_parse():
    "Basic parse operation."
    xml = '<b style="c">Some content</b>'
    root = parse(xml)
    assert root.tag == "b"
    assert root["style"] == "c"

def test_unparse():
    "Basic unparse operation."
    xml1 = '<b style="c">Some content</b>'
    root = parse(xml1)
    xml2 = unparse(root, indent=0, decl=None)
    assert xml1 == xml2

def test_indent():
    "Indentation."
    xml1 = '<b style="c">Some content<d>Another string</d></b>'
    root = parse(xml1)
    xml2 = '''<b style="c">Some content
  <d>Another string</d>
</b>'''
    xml3 = unparse(root, indent=2, decl=None)
    assert xml2 == xml3
    xml4 = unparse(root, indent=0, decl=None)
    assert xml1 == xml4

def test_file_like():
    "Use read/write with file-like objects."
    xml1 = '<b style="c">Some content<d>Another string</d></b>'
    infile = io.StringIO(xml1)
    root = read(infile)
    xml2 = unparse(root, decl=False)
    assert xml1 == xml2
    outfile = io.StringIO()
    write(outfile, root, decl=False)
    xml3 = outfile.getvalue()
    assert xml1 == xml3

def test_escape():
    "Escaping of characters that might cause XML problems."
    xml1 = '<b style="c" comparison="&gt;">Some content&lt;<d>Another string</d></b>'
    root1 = parse(xml1)
    assert root1["comparison"] == ">"
    xml2 = unparse(root1, decl=False)
    assert xml1 == xml2
    root2 = Element("b", "Some content<", style="c", comparison=">")
    root2.create("d").append("Another string")
    xml3 = unparse(root2, decl=False)
    assert xml1 == xml3
    
