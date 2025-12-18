import unittest

from textnode import TextNode, TextType
from htmlnode import HtmlNode, LeafNode, ParentNode


class TestTextNode(unittest.TestCase):
    def test_eq(self):
        node = TextNode("This is a text node", TextType.bold, None)
        node2 = TextNode("This is a text node", TextType.bold, None)
        self.assertEqual(node, node2)
        self.assertTrue(node == node2)
        self.assertFalse(node != node2)
        self.assertNotEqual(node, TextNode("Different text", TextType.bold, None))

    

if __name__ == "__main__":
    unittest.main()