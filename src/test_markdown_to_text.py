import unittest
from textnode import TextNode, TextType
from markdown_to_text import split_nodes_delimiter

class TestMarkdownToText(unittest.TestCase):
    def test_split_backtick_code(self):
        node = TextNode("This is text with a `code block` word", TextType.plaintext)
        new_nodes = split_nodes_delimiter([node], "`", TextType.codetext)
        texts = [(n.text, n.text_type) for n in new_nodes]
        expected = [
            ("This is text with a ", TextType.plaintext),
            ("code block", TextType.codetext),
            (" word", TextType.plaintext),
        ]
        self.assertEqual(texts, expected)

    def test_split_double_star_bold(self):
        node = TextNode("Make this **bold** please", TextType.plaintext)
        new_nodes = split_nodes_delimiter([node], "**", TextType.bold)
        texts = [(n.text, n.text_type) for n in new_nodes]
        expected = [
            ("Make this ", TextType.plaintext),
            ("bold", TextType.bold),
            (" please", TextType.plaintext),
        ]
        self.assertEqual(texts, expected)

    def test_unmatched_delimiter_raises(self):
        node = TextNode("This has `no close", TextType.plaintext)
        with self.assertRaises(Exception) as ctx:
            split_nodes_delimiter([node], "`", TextType.codetext)
        self.assertIn("Unmatched delimiter", str(ctx.exception))

    def test_non_plaintext_nodes_unchanged(self):
        node = TextNode("already bold", TextType.bold)
        out = split_nodes_delimiter([node], "**", TextType.bold)
        self.assertEqual(len(out), 1)
        self.assertIs(out[0], node)

    # NEW TESTS BELOW

    def test_split_asterisk_italic(self):
        node = TextNode("This is *italic* text", TextType.plaintext)
        new_nodes = split_nodes_delimiter([node], "*", TextType.italic)
        texts = [(n.text, n.text_type) for n in new_nodes]
        expected = [
            ("This is ", TextType.plaintext),
            ("italic", TextType.italic),
            (" text", TextType.plaintext),
        ]
        self.assertEqual(texts, expected)

    def test_multiple_delimiters(self):
        node = TextNode("This has **bold** and *italic* and `code`", TextType.plaintext)
        # Test bold first
        bold_nodes = split_nodes_delimiter([node], "**", TextType.bold)
        # Then italic on the result
        italic_nodes = split_nodes_delimiter(bold_nodes, "*", TextType.italic)
        # Then code on the result
        code_nodes = split_nodes_delimiter(italic_nodes, "`", TextType.codetext)
        
        texts = [(n.text, n.text_type) for n in code_nodes]
        expected = [
            ("This has ", TextType.plaintext),
            ("bold", TextType.bold),
            (" and ", TextType.plaintext),
            ("italic", TextType.italic),
            (" and ", TextType.plaintext),
            ("code", TextType.codetext),
        ]
        self.assertEqual(texts, expected)

    def test_empty_string(self):
        node = TextNode("", TextType.plaintext)
        new_nodes = split_nodes_delimiter([node], "**", TextType.bold)
        self.assertEqual(len(new_nodes), 1)
        self.assertEqual(new_nodes[0].text, "")
        self.assertEqual(new_nodes[0].text_type, TextType.plaintext)

    def test_only_delimited_content(self):
        node = TextNode("**bold only**", TextType.plaintext)
        new_nodes = split_nodes_delimiter([node], "**", TextType.bold)
        texts = [(n.text, n.text_type) for n in new_nodes]
        expected = [
            ("bold only", TextType.bold),
        ]
        self.assertEqual(texts, expected)

    def test_delimiter_at_start(self):
        node = TextNode("**bold** at start", TextType.plaintext)
        new_nodes = split_nodes_delimiter([node], "**", TextType.bold)
        texts = [(n.text, n.text_type) for n in new_nodes]
        expected = [
            ("bold", TextType.bold),
            (" at start", TextType.plaintext),
        ]
        self.assertEqual(texts, expected)

    def test_delimiter_at_end(self):
        node = TextNode("text at end **bold**", TextType.plaintext)
        new_nodes = split_nodes_delimiter([node], "**", TextType.bold)
        texts = [(n.text, n.text_type) for n in new_nodes]
        expected = [
            ("text at end ", TextType.plaintext),
            ("bold", TextType.bold),
        ]
        self.assertEqual(texts, expected)

    def test_consecutive_delimiters(self):
        node = TextNode("**bold****more bold**", TextType.plaintext)
        new_nodes = split_nodes_delimiter([node], "**", TextType.bold)
        texts = [(n.text, n.text_type) for n in new_nodes]
        expected = [
            ("bold", TextType.bold),
            ("more bold", TextType.bold),
        ]
        self.assertEqual(texts, expected)

    def test_nested_delimiters_different_types(self):
        node = TextNode("This is **bold with *italic* inside**", TextType.plaintext)
        # First split bold
        bold_nodes = split_nodes_delimiter([node], "**", TextType.bold)
        # Should get 2 nodes (not 3)
        self.assertEqual(len(bold_nodes), 2)
        self.assertEqual(bold_nodes[0].text, "This is ")
        self.assertEqual(bold_nodes[0].text_type, TextType.plaintext)
        self.assertEqual(bold_nodes[1].text, "bold with *italic* inside")
        self.assertEqual(bold_nodes[1].text_type, TextType.bold)

    def test_multiple_nodes_input(self):
        nodes = [
            TextNode("First **bold** text", TextType.plaintext),
            TextNode("Already italic", TextType.italic),
            TextNode("Second **bold** text", TextType.plaintext),
        ]
        new_nodes = split_nodes_delimiter(nodes, "**", TextType.bold)
        
        texts = [(n.text, n.text_type) for n in new_nodes]
        expected = [
            ("First ", TextType.plaintext),
            ("bold", TextType.bold),
            (" text", TextType.plaintext),
            ("Already italic", TextType.italic),
            ("Second ", TextType.plaintext),
            ("bold", TextType.bold),
            (" text", TextType.plaintext),
        ]
        self.assertEqual(texts, expected)

    def test_delimiter_with_spaces(self):
        node = TextNode("Text ** bold ** with spaces", TextType.plaintext)
        new_nodes = split_nodes_delimiter([node], "**", TextType.bold)
        texts = [(n.text, n.text_type) for n in new_nodes]
        expected = [
            ("Text ", TextType.plaintext),
            (" bold ", TextType.bold),  # Note: includes spaces
            (" with spaces", TextType.plaintext),
        ]
        self.assertEqual(texts, expected)

    def test_mixed_delimiters_in_text(self):
        node = TextNode("Some `code` and **bold** and *italic* text", TextType.plaintext)
        # We'll test one delimiter at a time as the function expects
        nodes = split_nodes_delimiter([node], "`", TextType.codetext)
        nodes = split_nodes_delimiter(nodes, "**", TextType.bold)
        nodes = split_nodes_delimiter(nodes, "*", TextType.italic)
        
        texts = [(n.text, n.text_type) for n in nodes]
        expected = [
            ("Some ", TextType.plaintext),
            ("code", TextType.codetext),
            (" and ", TextType.plaintext),
            ("bold", TextType.bold),
            (" and ", TextType.plaintext),
            ("italic", TextType.italic),
            (" text", TextType.plaintext),
        ]
        self.assertEqual(texts, expected)

    def test_unicode_characters(self):
        node = TextNode("Text with 🚀 **rocket** and 😊 **smile**", TextType.plaintext)
        new_nodes = split_nodes_delimiter([node], "**", TextType.bold)
        texts = [(n.text, n.text_type) for n in new_nodes]
        expected = [
            ("Text with 🚀 ", TextType.plaintext),
            ("rocket", TextType.bold),
            (" and 😊 ", TextType.plaintext),
            ("smile", TextType.bold),
        ]
        self.assertEqual(texts, expected)

    def test_special_characters_in_delimited_content(self):
        node = TextNode("Text with **<bold> & 'special' chars**", TextType.plaintext)
        new_nodes = split_nodes_delimiter([node], "**", TextType.bold)
        texts = [(n.text, n.text_type) for n in new_nodes]
        expected = [
            ("Text with ", TextType.plaintext),
            ("<bold> & 'special' chars", TextType.bold),
        ]
        self.assertEqual(texts, expected)

if __name__ == "__main__":
    unittest.main()