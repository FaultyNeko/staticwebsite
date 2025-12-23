"""Split plaintext `old_nodes` by `delimiter` and convert the delimited
segments into `text_type` nodes.

Only nodes with `TextType.plaintext` are inspected and potentially split.
All other nodes are appended unchanged.

If a matching closing delimiter is not found for a plaintext node, an
Exception is raised with a helpful message.
"""
from textnode import TextNode, TextType
import re


def split_nodes_delimiter(old_nodes, delimiter, text_type):
    new_nodes = []

    for node in old_nodes:
        # Only attempt to split plaintext nodes
        if node.text_type != TextType.plaintext:
            new_nodes.append(node)
            continue

        text = node.text
        i = 0
        dlen = len(delimiter)

        # Special case for empty string - add it as is
        if text == "":
            new_nodes.append(TextNode("", TextType.plaintext, node.url))
            continue

        while i < len(text):  
            # Find next delimiter
            idx = text.find(delimiter, i)
            
            # If no delimiter found
            if idx == -1:
                # Add remaining text if not empty
                remaining = text[i:]
                if remaining:
                    new_nodes.append(TextNode(remaining, TextType.plaintext, node.url))
                break
            
            # Add text before delimiter if not empty
            if idx > i:
                before = text[i:idx]
                new_nodes.append(TextNode(before, TextType.plaintext, node.url))
            
            # Find closing delimiter
            j = text.find(delimiter, idx + dlen)
            if j == -1:
                raise Exception(f"Unmatched delimiter '{delimiter}' in text: {text!r}")
            
            # Add delimited content
            inner = text[idx + dlen:j]
            new_nodes.append(TextNode(inner, text_type, node.url))
            
            # Move past the closing delimiter
            i = j + dlen
            
            # If i == len(text), we're done, no need to add empty node

    return new_nodes

def extract_markdown_images(text):
    pattern = re.compile(r"!\[([^\[\]]*)\]\(([^\(\)]*)\)")
    matches = pattern.findall(text)
    return [(alt, url) for (alt, url) in matches]

def extract_markdown_links(text):
    pattern = re.compile(r"(?<!!)\[([^\[\]]*)\]\(([^\(\)]*)\)")
    matches = pattern.findall(text)
    return [(anchor, link) for (anchor, link) in matches]

def split_nodes_image(old_nodes):
    new_nodes = []
    pattern = re.compile(r"!\[([^\[\]]*)\]\(([^\(\)]*)\)")
    
    for node in old_nodes:
        if node.text_type != TextType.plaintext:
            new_nodes.append(node)
            continue 
        
        text = node.text
        if text == "":
            new_nodes.append(TextNode("", TextType.plaintext, node.url))
            continue
        i = 0
        while i < len(text):
            match = pattern.search(text, i)
            if not match:
                remaining = text[i:]
                if remaining:
                    new_nodes.append(TextNode(remaining, TextType.plaintext, node.url))
                break
            
            start, end = match.span()
            if start > i:
                before = text[i:start]
                new_nodes.append(TextNode(before, TextType.plaintext, node.url))
            
            alt_text, url = match.groups()
            new_nodes.append(TextNode(alt_text, TextType.image, url))
            i = end
    
    return new_nodes

def split_nodes_link(old_nodes):
    new_nodes = []
    pattern = re.compile(r"(?<!!)\[([^\[\]]*)\]\(([^\(\)]*)\)")
    
    for node in old_nodes:
        if node.text_type != TextType.plaintext:
            new_nodes.append(node)
            continue 
        
        text = node.text
        if text == "":
            new_nodes.append(TextNode("", TextType.plaintext, node.url))
            continue
        i = 0
        while i < len(text):
            match = pattern.search(text, i)
            if not match:
                remaining = text[i:]
                if remaining:
                    new_nodes.append(TextNode(remaining, TextType.plaintext, node.url))
                break
            
            start, end = match.span()
            if start > i:
                before = text[i:start]
                new_nodes.append(TextNode(before, TextType.plaintext, node.url))
            
            anchor_text, url = match.groups()
            new_nodes.append(TextNode(anchor_text, TextType.link, url))
            i = end
    
    return new_nodes

def split_nodes_code(old_nodes):
    return split_nodes_delimiter(old_nodes, "`", TextType.codetext)

def split_nodes_bold(old_nodes):
    return split_nodes_delimiter(old_nodes, "**", TextType.bold)

def split_nodes_italic(old_nodes):
    return split_nodes_delimiter(old_nodes, "*", TextType.italic)

def text_to_textnodes(text):
    nodes = []
    nodes.append(TextNode(text, TextType.plaintext, None))

    nodes = split_nodes_code(nodes)
    nodes = split_nodes_image(nodes)
    nodes = split_nodes_link(nodes)
    nodes = split_nodes_bold(nodes)
    nodes = split_nodes_italic(nodes)

    return nodes