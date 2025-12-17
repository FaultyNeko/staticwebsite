from enum import Enum

class TextType(Enum):
    plaintext = "plaintext"
    bold = "bold"
    italic = "italic"
    codetext = "codetext"
    link = "link"
    image = "image"

class TextNode:
    def __init__(self, text, text_type, url):
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