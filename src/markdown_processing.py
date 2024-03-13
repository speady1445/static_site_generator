import re
from enum import Enum, auto

from htmlnode import ParentNode
from textnode import TextNode, TextType, text_node_to_html_node


class BlockType(Enum):
    PARAGRAPH = auto()
    HEADING = auto()
    CODE = auto()
    QUOTE = auto()
    UNORDERED_LIST = auto()
    ORDERED_LIST = auto()


def split_nodes_delimiter(
    old_nodes: list[TextNode], delimiter: str, text_type: TextType
) -> list[TextNode]:
    new_nodes = []
    for old_node in old_nodes:
        if old_node.text_type is not TextType.TEXT or delimiter not in old_node.text:
            new_nodes.append(old_node)
        else:
            parts = old_node.text.split(delimiter)
            if len(parts) % 2 == 0:
                raise ValueError(f"Invalid Markdown syntax: {old_node.text}")
            text_part = True
            for part in parts:
                if part != "":
                    new_nodes.append(
                        TextNode(part, TextType.TEXT if text_part else text_type)
                    )
                text_part = not text_part

    return new_nodes


def extract_markdown_images(text: str) -> list[tuple[str, str]]:
    return re.findall(r"!\[(.*?)\]\((.*?)\)", text)


def extract_markdown_links(text: str) -> list[tuple[str, str]]:
    return re.findall(r"\[(.*?)\]\((.*?)\)", text)


def split_nodes_image(old_nodes: list[TextNode]) -> list[TextNode]:
    new_nodes = []
    for old_node in old_nodes:
        if old_node.text_type is not TextType.TEXT:
            new_nodes.append(old_node)
            continue
        extracted_images = extract_markdown_images(old_node.text)
        if not extracted_images:
            new_nodes.append(old_node)
        else:
            original_text = old_node.text
            for alt, url in extracted_images:
                parts = original_text.split(f"![{alt}]({url})", 1)
                if parts[0]:
                    new_nodes.append(TextNode(parts[0], TextType.TEXT))
                new_nodes.append(TextNode(alt, TextType.IMAGE, url))
                original_text = parts[1]
            if parts[1]:
                new_nodes.append(TextNode(parts[1], TextType.TEXT))

    return new_nodes


def split_nodes_link(old_nodes: list[TextNode]) -> list[TextNode]:
    new_nodes = []
    for old_node in old_nodes:
        if old_node.text_type is not TextType.TEXT:
            new_nodes.append(old_node)
            continue
        extracted_images = extract_markdown_links(old_node.text)
        if not extracted_images:
            new_nodes.append(old_node)
        else:
            original_text = old_node.text
            for alt, url in extracted_images:
                parts = original_text.split(f"[{alt}]({url})", 1)
                if parts[0]:
                    new_nodes.append(TextNode(parts[0], TextType.TEXT))
                new_nodes.append(TextNode(alt, TextType.LINK, url))
                original_text = parts[1]
            if parts[1]:
                new_nodes.append(TextNode(parts[1], TextType.TEXT))

    return new_nodes


def text_to_textnodes(text: str) -> list[TextNode]:
    nodes = [TextNode(text, TextType.TEXT)]
    for delimiter, type in (
        ("**", TextType.BOLD),
        ("*", TextType.ITALIC),
        ("`", TextType.CODE),
    ):
        nodes = split_nodes_delimiter(nodes, delimiter, type)

    nodes = split_nodes_image(nodes)
    nodes = split_nodes_link(nodes)

    return nodes


def markdown_to_blocks(markdown: str) -> list[str]:
    return [s.strip() for s in markdown.split("\n\n") if s != ""]


def block_to_block_type(block: str) -> BlockType:
    lines = block.split("\n")
    if (
        block.startswith("# ")
        or block.startswith("## ")
        or block.startswith("### ")
        or block.startswith("#### ")
        or block.startswith("##### ")
        or block.startswith("###### ")
    ):
        return BlockType.HEADING
    if block.startswith("```") and block.endswith("```"):
        return BlockType.CODE
    if block.startswith(">"):
        for line in lines:
            if not line.startswith(">"):
                return BlockType.PARAGRAPH
        return BlockType.QUOTE
    if block.startswith("* "):
        for line in lines:
            if not line.startswith("* "):
                return BlockType.PARAGRAPH
        return BlockType.UNORDERED_LIST
    if block.startswith("- "):
        for line in lines:
            if not line.startswith("- "):
                return BlockType.PARAGRAPH
        return BlockType.UNORDERED_LIST
    if block.startswith("1. "):
        i = 1
        for line in lines:
            if not line.startswith(f"{i}. "):
                return BlockType.PARAGRAPH
            i += 1
        return BlockType.ORDERED_LIST
    return BlockType.PARAGRAPH


def markdown_block_to_html_node(tag: str, markdown: str) -> ParentNode:
    return ParentNode(
        tag, [text_node_to_html_node(x) for x in text_to_textnodes(markdown)]
    )


def heading_to_html_node(heading: str) -> ParentNode:
    tag_text, text = heading.split(" ", 1)
    tag = f"h{len(tag_text)}"
    return markdown_block_to_html_node(tag, text)


def code_to_html_node(code: str) -> ParentNode:
    text = code[3:-3]
    return ParentNode("pre", [markdown_block_to_html_node("code", text)])


def quote_to_html_node(quote: str) -> ParentNode:
    text = " ".join([s[2:] for s in quote.split("\n")])
    return markdown_block_to_html_node("blockquote", text)


def unordered_list_to_html_node(unordered_list: str) -> ParentNode:
    items = [s[2:] for s in unordered_list.split("\n")]
    return ParentNode("ul", [markdown_block_to_html_node("li", item) for item in items])


def ordered_list_to_html_node(ordered_list: str) -> ParentNode:
    items = [s[s.find(" ") + 1 :] for s in ordered_list.split("\n")]
    return ParentNode("ol", [markdown_block_to_html_node("li", item) for item in items])


def paragraph_to_htmlnode(paragraph: str) -> ParentNode:
    return markdown_block_to_html_node("p", " ".join(paragraph.split("\n")))


def markdown_to_html_node(markdown: str) -> ParentNode:
    nodes = []
    for block in markdown_to_blocks(markdown):
        block_type = block_to_block_type(block)
        if block_type is BlockType.HEADING:
            nodes.append(heading_to_html_node(block))
        elif block_type is BlockType.CODE:
            nodes.append(code_to_html_node(block))
        elif block_type is BlockType.QUOTE:
            nodes.append(quote_to_html_node(block))
        elif block_type is BlockType.UNORDERED_LIST:
            nodes.append(unordered_list_to_html_node(block))
        elif block_type is BlockType.ORDERED_LIST:
            nodes.append(ordered_list_to_html_node(block))
        else:
            nodes.append(paragraph_to_htmlnode(block))
    return ParentNode("div", nodes)


def extract_title(markdown: str) -> str:
    blocks = markdown_to_blocks(markdown)
    for block in blocks:
        if block.startswith("# "):
            return block[2:]
    raise ValueError("Markdown does not contain a title")
