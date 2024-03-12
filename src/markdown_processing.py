import re
from enum import Enum, auto

from .textnode import TextNode, TextType


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


def text_to_textnode(text: str) -> list[TextNode]:
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
