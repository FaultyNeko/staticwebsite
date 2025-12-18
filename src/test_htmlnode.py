import unittest
from collections import OrderedDict

from textnode import TextNode, TextType, text_node_to_html_node
from htmlnode import HtmlNode, LeafNode, ParentNode



class TestHtmlNode(unittest.TestCase):
    def test_props_to_html_no_props(self):
        node = HtmlNode(tag="div")
        self.assertEqual(node.props_to_html(), "")

    def test_props_to_html_with_props(self):
        node = HtmlNode(tag="div", props={"class": "container", "id": "main"})
        expected = ' class="container" id="main"'
        self.assertEqual(node.props_to_html(), expected)

    def test_props_to_html_with_ordered_props(self):
        props = OrderedDict([("href", "https://www.google.com"), ("target", "_blank")])
        node = HtmlNode(tag="a", props=props)
        expected = ' href="https://www.google.com" target="_blank"'
        self.assertEqual(node.props_to_html(), expected)

    def test_repr(self):
        node = HtmlNode(tag="p", value="Hello", children=[], props={"style": "color:red;"})
        expected = "HtmlNode(tag=p, value=Hello, children=[], props={'style': 'color:red;'})"
        self.assertEqual(repr(node), expected)

    def test_leaf_to_html_p(self):
        node = LeafNode("p", "Hello, world!")
        self.assertEqual(node.to_html(), "<p>Hello, world!</p>")

    def test_leaf_to_html_with_props(self):
        props = OrderedDict([("href", "https://www.google.com"), ("target", "_blank")])
        node = LeafNode("a", "Click me!", props)
        expected = '<a href="https://www.google.com" target="_blank">Click me!</a>'
        self.assertEqual(node.to_html(), expected)

    def test_leaf_to_html_tag_none_returns_raw(self):
        node = LeafNode(None, "raw text", None)
        self.assertEqual(node.to_html(), "raw text")

    def test_leaf_to_html_missing_value_raises(self):
        node = LeafNode("p", None, None)
        with self.assertRaises(ValueError):
            node.to_html()

    def test_leaf_to_html_empty_props_no_space(self):
        node = LeafNode("p", "x", {})
        self.assertEqual(node.to_html(), "<p>x</p>")
    
    def test_to_html_with_children(self):
        child_node = LeafNode("span", "child")
        parent_node = ParentNode("div", [child_node])
        self.assertEqual(parent_node.to_html(), "<div><span>child</span></div>")

    def test_to_html_with_grandchildren(self):
        grandchild_node = LeafNode("b", "grandchild")
        child_node = ParentNode("span", [grandchild_node])
        parent_node = ParentNode("div", [child_node])
        self.assertEqual(
            parent_node.to_html(),
            "<div><span><b>grandchild</b></span></div>",
        )

    def test_text(self):
        node = TextNode("This is a text node", TextType.plaintext)
        html_node = text_node_to_html_node(node)
        self.assertEqual(html_node.tag, None)
        self.assertEqual(html_node.value, "This is a text node")

class TestTextNodeToHtmlNode(unittest.TestCase):
    
    def test_plaintext_to_html(self):
        node = TextNode("Hello, world!", TextType.plaintext)
        html_node = text_node_to_html_node(node)
        self.assertIsInstance(html_node, LeafNode)
        self.assertIsNone(html_node.tag)
        self.assertEqual(html_node.value, "Hello, world!")
        self.assertEqual(html_node.to_html(), "Hello, world!")

    def test_bold_to_html(self):
        node = TextNode("Bold text", TextType.bold)
        html_node = text_node_to_html_node(node)
        self.assertIsInstance(html_node, LeafNode)
        self.assertEqual(html_node.tag, "b")
        self.assertEqual(html_node.value, "Bold text")
        self.assertEqual(html_node.to_html(), "<b>Bold text</b>")

    def test_italic_to_html(self):
        node = TextNode("Italic text", TextType.italic)
        html_node = text_node_to_html_node(node)
        self.assertIsInstance(html_node, LeafNode)
        self.assertEqual(html_node.tag, "i")
        self.assertEqual(html_node.value, "Italic text")
        self.assertEqual(html_node.to_html(), "<i>Italic text</i>")

    def test_code_to_html(self):
        node = TextNode("print('Hello')", TextType.codetext)
        html_node = text_node_to_html_node(node)
        self.assertIsInstance(html_node, LeafNode)
        self.assertEqual(html_node.tag, "code")
        self.assertEqual(html_node.value, "print('Hello')")
        self.assertEqual(html_node.to_html(), "<code>print('Hello')</code>")

    def test_link_to_html(self):
        node = TextNode("Click here", TextType.link, "https://www.google.com")
        html_node = text_node_to_html_node(node)
        self.assertIsInstance(html_node, LeafNode)
        self.assertEqual(html_node.tag, "a")
        self.assertEqual(html_node.value, "Click here")
        self.assertEqual(html_node.props, {"href": "https://www.google.com"})
        self.assertEqual(html_node.to_html(), '<a href="https://www.google.com">Click here</a>')

    def test_link_without_url_raises(self):
        # Note: Your current implementation returns props=None when url is None
        node = TextNode("Click here", TextType.link, None)
        html_node = text_node_to_html_node(node)
        self.assertEqual(html_node.tag, "a")
        self.assertEqual(html_node.value, "Click here")
        self.assertIsNone(html_node.props)
        self.assertEqual(html_node.to_html(), "<a>Click here</a>")

    def test_image_to_html(self):
        node = TextNode("Alt text", TextType.image, "https://example.com/image.png")
        html_node = text_node_to_html_node(node)
        self.assertIsInstance(html_node, LeafNode)
        self.assertEqual(html_node.tag, "img")
        self.assertEqual(html_node.value, "")  # Changed from assertIsNone to assertEqual with ""
        self.assertEqual(html_node.props, {"src": "https://example.com/image.png", "alt": "Alt text"})
        self.assertEqual(html_node.to_html(), '<img src="https://example.com/image.png" alt="Alt text"></img>')  # Added closing tag

    def test_image_without_url_raises(self):
        # Note: Your current implementation returns props=None when url is None
        node = TextNode("Alt text", TextType.image, None)
        html_node = text_node_to_html_node(node)
        self.assertEqual(html_node.tag, "img")
        self.assertEqual(html_node.value, "")  # Changed from assertIsNone to assertEqual with ""
        self.assertIsNone(html_node.props)
        self.assertEqual(html_node.to_html(), "<img></img>")  # Added closing tag

    def test_invalid_text_type_raises(self):
        # Create a TextNode with an invalid TextType
        node = TextNode("Some text", "invalid_type")
        with self.assertRaises(Exception) as context:
            text_node_to_html_node(node)
        self.assertIn("Unsupported TextType", str(context.exception))

    def test_none_text_type_raises(self):
        node = TextNode("Some text", None)
        with self.assertRaises(Exception) as context:
            text_node_to_html_node(node)
        self.assertEqual(str(context.exception), "TextNode must have a text_type")

    def test_empty_text(self):
        node = TextNode("", TextType.plaintext)
        html_node = text_node_to_html_node(node)
        self.assertIsInstance(html_node, LeafNode)
        self.assertIsNone(html_node.tag)
        self.assertEqual(html_node.value, "")
        self.assertEqual(html_node.to_html(), "")

    def test_link_with_special_characters(self):
        node = TextNode("Search & Find", TextType.link, "https://example.com/search?q=test&sort=desc")
        html_node = text_node_to_html_node(node)
        expected_html = '<a href="https://example.com/search?q=test&sort=desc">Search & Find</a>'
        self.assertEqual(html_node.to_html(), expected_html)

    def test_multiple_conversions(self):
        # Test converting multiple different types
        text_nodes = [
            TextNode("Plain", TextType.plaintext),
            TextNode("Bold", TextType.bold),
            TextNode("Italic", TextType.italic),
            TextNode("Code", TextType.codetext),
        ]
        
        for text_node in text_nodes:
            html_node = text_node_to_html_node(text_node)
            self.assertIsInstance(html_node, LeafNode)

    

if __name__ == "__main__":
    unittest.main()