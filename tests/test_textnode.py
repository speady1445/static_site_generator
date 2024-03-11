import unittest

from src.htmlnode import LeafNode
from src.textnode import TextNode, TextType, text_node_to_html_node


class TestTextNode(unittest.TestCase):
    def test_eq(self):
        node = TextNode("This is a text node", TextType.BOLD)
        node2 = TextNode("This is a text node", TextType.BOLD)
        self.assertEqual(node, node2)

    def test_not_qe_text(self):
        node = TextNode("This is a text node", TextType.BOLD)
        node2 = TextNode("This is a different text node", TextType.BOLD)
        self.assertNotEqual(node, node2)

    def test_not_qe_text_type(self):
        node = TextNode("This is a text node", TextType.BOLD)
        node2 = TextNode("This is a text node", TextType.ITALIC)
        self.assertNotEqual(node, node2)

    def test_not_qe_url(self):
        node = TextNode("This is a text node", TextType.BOLD, "https://www.example.com")
        node2 = TextNode("This is a text node", TextType.BOLD, "https://example.com")
        self.assertNotEqual(node, node2)

    def test_repr(self):
        node = TextNode("This is a text node", TextType.BOLD, "https://www.example.com")
        self.assertEqual(
            repr(node), "TextNode(This is a text node, bold, https://www.example.com)"
        )


class TestTextNodeToHtmlNode(unittest.TestCase):
    def test_text_node(self):
        node = TextNode("This is a text node", TextType.TEXT)
        self.assertEqual(
            text_node_to_html_node(node), LeafNode(None, "This is a text node")
        )

    def test_bold_node(self):
        node = TextNode("This is a bold node", TextType.BOLD)
        self.assertEqual(
            text_node_to_html_node(node), LeafNode("b", "This is a bold node")
        )

    def test_italic_node(self):
        node = TextNode("This is a italic node", TextType.ITALIC)
        self.assertEqual(
            text_node_to_html_node(node), LeafNode("i", "This is a italic node")
        )

    def test_code_node(self):
        node = TextNode("This is a code node", TextType.CODE)
        self.assertEqual(
            text_node_to_html_node(node), LeafNode("code", "This is a code node")
        )

    def test_link_node(self):
        node = TextNode("This is a link node", TextType.LINK, "https://www.example.com")
        self.assertEqual(
            text_node_to_html_node(node),
            LeafNode("a", "This is a link node", {"href": "https://www.example.com"}),
        )

    def test_link_node_no_url(self):
        node = TextNode("This is a link node", TextType.LINK)
        self.assertRaises(ValueError, text_node_to_html_node, node)

    def test_image_node(self):
        node = TextNode("This is an image node", TextType.IMAGE, "abc.jpg")
        self.assertEqual(
            text_node_to_html_node(node),
            LeafNode("img", "", {"src": "abc.jpg", "alt": "This is an image node"}),
        )

    def test_image_node_no_url(self):
        node = TextNode("This is an image node", TextType.IMAGE)
        self.assertRaises(ValueError, text_node_to_html_node, node)

    def test_unknown_type(self):
        node = TextNode("This is an image node", "unknown")  # type: ignore
        self.assertRaises(ValueError, text_node_to_html_node, node)


if __name__ == "__main__":
    unittest.main()
