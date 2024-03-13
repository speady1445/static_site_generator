import unittest

from htmlnode import HTMLNode, LeafNode, ParentNode


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


class TestParentNode(unittest.TestCase):
    def test_to_html_no_tag(self):
        node = ParentNode(None, [])  # type: ignore
        self.assertRaises(ValueError, node.to_html)

    def test_to_html_no_children(self):
        node = ParentNode("div", None)  # type: ignore
        self.assertRaises(ValueError, node.to_html)

    def test_to_html_with_children(self):
        node = ParentNode("div", [LeafNode("p", "This is a text node")])
        self.assertEqual(node.to_html(), "<div><p>This is a text node</p></div>")

    def test_to_html_nested(self):
        node = ParentNode(
            "div",
            [
                ParentNode("ul", [LeafNode("li", "Item 1"), LeafNode("li", "Item 2")]),
            ],
        )
        self.assertEqual(
            node.to_html(), "<div><ul><li>Item 1</li><li>Item 2</li></ul></div>"
        )

    def test_to_html_many_children(self):
        node = ParentNode(
            "div",
            [
                LeafNode("p", "Text1"),
                LeafNode(None, "Text2 without tag"),
                LeafNode("p", "Text3"),
            ],
        )
        self.assertEqual(
            node.to_html(), "<div><p>Text1</p>Text2 without tag<p>Text3</p></div>"
        )
