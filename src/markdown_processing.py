import re

from .textnode import TextNode, TextType


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
