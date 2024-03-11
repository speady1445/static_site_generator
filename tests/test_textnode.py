import unittest

from src.htmlnode import LeafNode
from src.textnode import (
    TextNode,
    TextType,
    extract_markdown_images,
    extract_markdown_links,
    split_nodes_delimiter,
    split_nodes_image,
    split_nodes_link,
    text_node_to_html_node,
)


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


class TestSplitNodesDelimiter(unittest.TestCase):
    def test_without_delimiter(self):
        node = TextNode("This is a text node", TextType.TEXT)
        self.assertEqual([node], split_nodes_delimiter([node], "*", TextType.ITALIC))

    def test_with_odd_delimiters(self):
        node = TextNode("This is *a text node", TextType.TEXT)
        self.assertRaises(
            ValueError, split_nodes_delimiter, [node], "*", TextType.ITALIC
        )

    def test_with_odd_delimiters2(self):
        node = TextNode("This is *a* *text node", TextType.TEXT)
        self.assertRaises(
            ValueError, split_nodes_delimiter, [node], "*", TextType.ITALIC
        )

    def test_even_delimiter(self):
        node = TextNode("This is *a* text node", TextType.TEXT)
        self.assertEqual(
            [
                TextNode("This is ", TextType.TEXT),
                TextNode("a", TextType.ITALIC),
                TextNode(" text node", TextType.TEXT),
            ],
            split_nodes_delimiter([node], "*", TextType.ITALIC),
        )

    def test_even_delimiter2(self):
        node = TextNode("This is *a* *text* node", TextType.TEXT)
        self.assertEqual(
            [
                TextNode("This is ", TextType.TEXT),
                TextNode("a", TextType.ITALIC),
                TextNode(" ", TextType.TEXT),
                TextNode("text", TextType.ITALIC),
                TextNode(" node", TextType.TEXT),
            ],
            split_nodes_delimiter([node], "*", TextType.ITALIC),
        )

    def test_longer_delimiter(self):
        node = TextNode("This is a **text** node", TextType.TEXT)
        self.assertEqual(
            [
                TextNode("This is a ", TextType.TEXT),
                TextNode("text", TextType.BOLD),
                TextNode(" node", TextType.TEXT),
            ],
            split_nodes_delimiter([node], "**", TextType.BOLD),
        )

    def test_multiword(self):
        node = TextNode("This `is a code` node", TextType.TEXT)
        self.assertEqual(
            [
                TextNode("This ", TextType.TEXT),
                TextNode("is a code", TextType.CODE),
                TextNode(" node", TextType.TEXT),
            ],
            split_nodes_delimiter([node], "`", TextType.CODE),
        )


class TestMarkdownExtractions(unittest.TestCase):
    def test_images(self):
        self.assertEqual(
            extract_markdown_images(
                (
                    "This is text with an ![image](https://i.imgur.com/zjjcJKZ.png) and"
                    " ![another](https://i.imgur.com/dfsdkjfd.png)"
                )
            ),
            [
                ("image", "https://i.imgur.com/zjjcJKZ.png"),
                ("another", "https://i.imgur.com/dfsdkjfd.png"),
            ],
        )

    def test_links(self):
        self.assertEqual(
            extract_markdown_links(
                (
                    "This is text with a [link](https://www.example.com) and"
                    " [another](https://www.example.com/another)"
                )
            ),
            [
                ("link", "https://www.example.com"),
                ("another", "https://www.example.com/another"),
            ],
        )


class TestSplitImage(unittest.TestCase):
    def test_no_image(self):
        node = TextNode("This is text", TextType.TEXT)
        self.assertEqual(split_nodes_image([node]), [node])

    def test_split_just_image(self):
        node = TextNode("![alt text](https://some.img.com/abc.png)", TextType.TEXT)
        self.assertEqual(
            split_nodes_image([node]),
            [TextNode("alt text", TextType.IMAGE, "https://some.img.com/abc.png")],
        )

    def test_split_within_text(self):
        node = TextNode(
            "This ![alt text](https://some.img.com/abc.png) is text", TextType.TEXT
        )
        self.assertEqual(
            split_nodes_image([node]),
            [
                TextNode("This ", TextType.TEXT),
                TextNode("alt text", TextType.IMAGE, "https://some.img.com/abc.png"),
                TextNode(" is text", TextType.TEXT),
            ],
        )

    def test_split_multiple_images(self):
        node = TextNode(
            (
                "This ![alt text](https://some.img.com/abc.png) and"
                " ![another](https://some.img.com/def.png) is text"
            ),
            TextType.TEXT,
        )
        self.assertEqual(
            split_nodes_image([node]),
            [
                TextNode("This ", TextType.TEXT),
                TextNode("alt text", TextType.IMAGE, "https://some.img.com/abc.png"),
                TextNode(" and ", TextType.TEXT),
                TextNode("another", TextType.IMAGE, "https://some.img.com/def.png"),
                TextNode(" is text", TextType.TEXT),
            ],
        )


class TestSplitLink(unittest.TestCase):
    def test_no_link(self):
        node = TextNode("This is text", TextType.TEXT)
        self.assertEqual(split_nodes_link([node]), [node])

    def test_split_just_link(self):
        node = TextNode("[qwer](https://www.example.com)", TextType.TEXT)
        self.assertEqual(
            split_nodes_link([node]),
            [TextNode("qwer", TextType.LINK, "https://www.example.com")],
        )

    def test_split_within_text(self):
        node = TextNode("This [qwer](https://www.example.com) is text", TextType.TEXT)
        self.assertEqual(
            split_nodes_link([node]),
            [
                TextNode("This ", TextType.TEXT),
                TextNode("qwer", TextType.LINK, "https://www.example.com"),
                TextNode(" is text", TextType.TEXT),
            ],
        )

    def test_split_multiple_links(self):
        node = TextNode(
            (
                "This [first](https://some.img.com/abc.png) and"
                " [second](https://some.img.com/def.png) is text"
            ),
            TextType.TEXT,
        )
        self.assertEqual(
            split_nodes_link([node]),
            [
                TextNode("This ", TextType.TEXT),
                TextNode("first", TextType.LINK, "https://some.img.com/abc.png"),
                TextNode(" and ", TextType.TEXT),
                TextNode("second", TextType.LINK, "https://some.img.com/def.png"),
                TextNode(" is text", TextType.TEXT),
            ],
        )


if __name__ == "__main__":
    unittest.main()
