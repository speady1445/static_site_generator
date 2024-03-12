import unittest

from src.markdown_processing import (
    BlockType,
    block_to_block_type,
    extract_markdown_images,
    extract_markdown_links,
    markdown_to_blocks,
    split_nodes_delimiter,
    split_nodes_image,
    split_nodes_link,
    text_to_textnode,
)
from src.textnode import TextNode, TextType


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


class TestTextToTextnode(unittest.TestCase):
    def test_empty(self):
        self.assertEqual(text_to_textnode(""), [TextNode("", TextType.TEXT)])

    def test_everything(self):
        text = (
            "This is **text** with an *italic* word"
            " and a `code block` and an ![image](https://i.imgur.com/zjjcJKZ.png)"
            " and a [link](https://boot.dev). And some more."
        )
        self.assertEqual(
            text_to_textnode(text),
            [
                TextNode("This is ", TextType.TEXT),
                TextNode("text", TextType.BOLD),
                TextNode(" with an ", TextType.TEXT),
                TextNode("italic", TextType.ITALIC),
                TextNode(" word and a ", TextType.TEXT),
                TextNode("code block", TextType.CODE),
                TextNode(" and an ", TextType.TEXT),
                TextNode("image", TextType.IMAGE, "https://i.imgur.com/zjjcJKZ.png"),
                TextNode(" and a ", TextType.TEXT),
                TextNode("link", TextType.LINK, "https://boot.dev"),
                TextNode(". And some more.", TextType.TEXT),
            ],
        )


class TestMarkdownToBlocks(unittest.TestCase):
    def test_three_blocks(self):
        text = """
This is **bolded** paragraph

This is another paragraph with *italic* text and `code` here
This is the same paragraph on a new line

* This is a list
* with items
"""
        self.assertEqual(
            markdown_to_blocks(text),
            [
                "This is **bolded** paragraph",
                (
                    "This is another paragraph with *italic* text and `code` here\n"
                    "This is the same paragraph on a new line"
                ),
                "* This is a list\n* with items",
            ],
        )

    def test_excesive_newlines(self):
        text = """
This is **bolded** paragraph






This is another paragraph with *italic* text and `code` here
"""
        self.assertEqual(
            markdown_to_blocks(text),
            [
                "This is **bolded** paragraph",
                "This is another paragraph with *italic* text and `code` here",
            ],
        )


class TestBlockToBlockType(unittest.TestCase):
    def test_paragraph(self):
        self.assertEqual(
            block_to_block_type("This is a paragraph"), BlockType.PARAGRAPH
        )

    def test_heading_1(self):
        self.assertEqual(block_to_block_type("# This is a heading"), BlockType.HEADING)

    def test_heading2(self):
        self.assertEqual(block_to_block_type("## This is a heading"), BlockType.HEADING)

    def test_heading3(self):
        self.assertEqual(
            block_to_block_type("### This is a heading"), BlockType.HEADING
        )

    def test_heading4(self):
        self.assertEqual(
            block_to_block_type("#### This is a heading"), BlockType.HEADING
        )

    def test_heading5(self):
        self.assertEqual(
            block_to_block_type("##### This is a heading"), BlockType.HEADING
        )

    def test_heading6(self):
        self.assertEqual(
            block_to_block_type("###### This is a heading"), BlockType.HEADING
        )

    def test_not_heading(self):
        self.assertEqual(
            block_to_block_type("####### This is a heading"), BlockType.PARAGRAPH
        )

    def test_code(self):
        self.assertEqual(block_to_block_type("```code```"), BlockType.CODE)

    def test_quote(self):
        self.assertEqual(block_to_block_type("> This is a quote"), BlockType.QUOTE)

    def test_unordered_list(self):
        self.assertEqual(
            block_to_block_type("* This is an unordered list\n* with items"),
            BlockType.UNORDERED_LIST,
        )

    def test_ordered_list(self):
        self.assertEqual(
            block_to_block_type("1. This is an ordered list\n2. with items"),
            BlockType.ORDERED_LIST,
        )

    def test_ordered_list_wrong_order(self):
        self.assertEqual(
            block_to_block_type("2. This is an ordered list\n1. with items"),
            BlockType.PARAGRAPH,
        )
