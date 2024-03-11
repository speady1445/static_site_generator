import unittest

from src.htmlnode import HTMLNode


class TextHTMLNode(unittest.TestCase):
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
