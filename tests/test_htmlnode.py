import unittest

from src.htmlnode import HTMLNode, LeafNode


class TestHTMLNode(unittest.TestCase):
    def test_to_html(self):
        node = HTMLNode()
        self.assertRaises(NotImplementedError, node.to_html)

    def test_props_to_html(self):
        node = HTMLNode(props={"prop1": "value1", "prop2": "value2"})
        self.assertEqual(node.props_to_html(), ' prop1="value1" prop2="value2"')

    def test_repr(self):
        node = HTMLNode(
            tag="div",
            value="This is a text node",
            children=[],
            props={"prop1": "value1"},
        )
        self.assertEqual(
            repr(node), "HTMLNode(div, This is a text node, [], {'prop1': 'value1'})"
        )


class TestLeafNode(unittest.TestCase):
    def test_to_html_no_tag(self):
        node = LeafNode(None, "This is a text node")
        self.assertEqual(node.to_html(), "This is a text node")

    def test_to_html(self):
        node = LeafNode("div", "This is a text node")
        self.assertEqual(node.to_html(), "<div>This is a text node</div>")

    def test_to_html_with_props(self):
        node = LeafNode("a", "Click me!", {"href": "https://www.google.com"})
        self.assertEqual(
            node.to_html(), '<a href="https://www.google.com">Click me!</a>'
        )
