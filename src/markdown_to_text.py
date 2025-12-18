"""Split plaintext `old_nodes` by `delimiter` and convert the delimited
segments into `text_type` nodes.

Only nodes with `TextType.plaintext` are inspected and potentially split.
All other nodes are appended unchanged.

If a matching closing delimiter is not found for a plaintext node, an
Exception is raised with a helpful message.
"""
from textnode import TextNode, TextType


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

        # Special case for empty string - add it as-is
        if text == "":
            new_nodes.append(TextNode("", TextType.plaintext, node.url))
            continue

        while i < len(text):  # Changed back to < not <=
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
            
            # Don't add empty node at the end!
            # If i == len(text), we're done, no need to add empty node

    return new_nodes