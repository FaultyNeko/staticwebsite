from enum import Enum
from htmlnode import LeafNode

class TextType(Enum):
    plaintext = "plaintext"
    bold = "bold"
    italic = "italic"
    codetext = "codetext"
    link = "link"
    image = "image"

class TextNode:
    def __init__(self, text, text_type, url = None):
        self.text = text
        self.text_type = text_type
        self.url = url

    def __eq__(self, other):
        if not isinstance(other, TextNode):
            return False
        return (self.text == other.text and
                self.text_type == other.text_type and
                self.url == other.url)
    def __repr__(self):
        return f"TextNode(text={self.text}, text_type={self.text_type}, url={self.url})"

def text_node_to_html_node(text_node):
    if text_node.text_type == None:
        raise Exception("TextNode must have a text_type")
    else:
        if text_node.text_type == TextType.plaintext:
            return LeafNode(tag=None, value=text_node.text, props=None)
        elif text_node.text_type == TextType.bold:
            return LeafNode(tag="b", value=text_node.text, props=None)
        elif text_node.text_type == TextType.italic:
            return LeafNode(tag="i", value=text_node.text, props=None)
        elif text_node.text_type == TextType.codetext:
            return LeafNode(tag="code", value=text_node.text, props=None)
        elif text_node.text_type == TextType.link:
            return LeafNode(tag="a", value=text_node.text, props={"href": text_node.url} if text_node.url else None)
        elif text_node.text_type == TextType.image:
            return LeafNode(tag="img", value="", props={"src": text_node.url, "alt": text_node.text} if text_node.url else None)
        else:
            raise Exception(f"Unsupported TextType: {text_node.text_type}")
