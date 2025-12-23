import unittest
from textnode import TextNode, TextType
from markdown_to_text import split_nodes_delimiter, extract_markdown_images, extract_markdown_links, split_nodes_image, split_nodes_link, text_to_textnodes


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

class TestExtractMarkdownImages(unittest.TestCase):
    def test_single_image(self):
        text = "This is text with an ![image](https://i.imgur.com/zjjcJKZ.png)"
        result = extract_markdown_images(text)
        expected = [("image", "https://i.imgur.com/zjjcJKZ.png")]
        self.assertEqual(result, expected)

    def test_multiple_images(self):
        text = "![first](https://first.com) and ![second](https://second.com)"
        result = extract_markdown_images(text)
        expected = [
            ("first", "https://first.com"),
            ("second", "https://second.com")
        ]
        self.assertEqual(result, expected)

    def test_image_with_spaces_in_alt(self):
        text = "![alt text with spaces](https://example.com/image.png)"
        result = extract_markdown_images(text)
        expected = [("alt text with spaces", "https://example.com/image.png")]
        self.assertEqual(result, expected)

    def test_image_with_special_chars(self):
        text = "![alt-text_with.dots&dashes](https://example.com/img-1.jpg)"
        result = extract_markdown_images(text)
        expected = [("alt-text_with.dots&dashes", "https://example.com/img-1.jpg")]
        self.assertEqual(result, expected)

    def test_no_images(self):
        text = "This is just plain text with no images"
        result = extract_markdown_images(text)
        self.assertEqual(result, [])

    def test_empty_alt_text(self):
        text = "![](https://example.com/blank.png)"
        result = extract_markdown_images(text)
        expected = [("", "https://example.com/blank.png")]
        self.assertEqual(result, expected)

    def test_image_in_middle_of_text(self):
        text = "Text before ![middle](mid.jpg) text after"
        result = extract_markdown_images(text)
        expected = [("middle", "mid.jpg")]
        self.assertEqual(result, expected)

    def test_multiple_lines(self):
        text = """First line with ![img1](url1)
Second line with ![img2](url2)
Third line with no image"""
        result = extract_markdown_images(text)
        expected = [
            ("img1", "url1"),
            ("img2", "url2")
        ]
        self.assertEqual(result, expected)

    def test_url_with_query_params(self):
        text = "![query](https://example.com/image.jpg?width=100&height=200)"
        result = extract_markdown_images(text)
        expected = [("query", "https://example.com/image.jpg?width=100&height=200")]
        self.assertEqual(result, expected)

    def test_does_not_capture_links(self):
        text = "This is a [link](https://example.com) not an image"
        result = extract_markdown_images(text)
        self.assertEqual(result, [])

    def test_mixed_images_and_links(self):
        text = "![image](img.jpg) and [link](https://example.com)"
        result = extract_markdown_images(text)
        expected = [("image", "img.jpg")]
        self.assertEqual(result, expected)

class TestExtractMarkdownLinks(unittest.TestCase):
    def test_single_link(self):
        text = "This is text with a [link](https://www.example.com)"
        result = extract_markdown_links(text)
        expected = [("link", "https://www.example.com")]
        self.assertEqual(result, expected)

    def test_multiple_links(self):
        text = "[first](https://first.com) and [second](https://second.com)"
        result = extract_markdown_links(text)
        expected = [
            ("first", "https://first.com"),
            ("second", "https://second.com")
        ]
        self.assertEqual(result, expected)

    def test_link_with_spaces_in_text(self):
        text = "[link text with spaces](https://example.com)"
        result = extract_markdown_links(text)
        expected = [("link text with spaces", "https://example.com")]
        self.assertEqual(result, expected)

    def test_no_links(self):
        text = "This is just plain text with no links"
        result = extract_markdown_links(text)
        self.assertEqual(result, [])

    def test_empty_link_text(self):
        text = "[](https://example.com)"
        result = extract_markdown_links(text)
        expected = [("", "https://example.com")]
        self.assertEqual(result, expected)

    def test_link_in_middle_of_text(self):
        text = "Text before [middle](mid.html) text after"
        result = extract_markdown_links(text)
        expected = [("middle", "mid.html")]
        self.assertEqual(result, expected)

    def test_does_not_capture_images(self):
        text = "This is an ![image](https://example.com/img.jpg) not a link"
        result = extract_markdown_links(text)
        self.assertEqual(result, [])

    def test_mixed_links_and_images(self):
        text = "[link](page.html) and ![image](img.jpg)"
        result = extract_markdown_links(text)
        expected = [("link", "page.html")]
        self.assertEqual(result, expected)

    def test_link_with_special_chars(self):
        text = "[link-text_with.dots&dashes](https://example.com/page-1.html)"
        result = extract_markdown_links(text)
        expected = [("link-text_with.dots&dashes", "https://example.com/page-1.html")]
        self.assertEqual(result, expected)

    def test_relative_urls(self):
        text = "[about](/about) [contact](./contact.html)"
        result = extract_markdown_links(text)
        expected = [
            ("about", "/about"),
            ("contact", "./contact.html")
        ]
        self.assertEqual(result, expected)
class splitImagesNodes(unittest.TestCase):
    def test_single_image(self):
        node = TextNode(
            "This is text with an ![image](https://i.imgur.com/zjjcJKZ.png)",
            TextType.plaintext
        )
        new_nodes = split_nodes_image([node])
        expected = [
            TextNode("This is text with an ", TextType.plaintext),
            TextNode("image", TextType.image, "https://i.imgur.com/zjjcJKZ.png"),
        ]
        self.assertEqual(new_nodes, expected)

    def test_multiple_images(self):
        node = TextNode(
            "![first](https://first.com) and ![second](https://second.com)",
            TextType.plaintext
        )
        new_nodes = split_nodes_image([node])
        expected = [
            TextNode("first", TextType.image, "https://first.com"),
            TextNode(" and ", TextType.plaintext),
            TextNode("second", TextType.image, "https://second.com"),
        ]
        self.assertEqual(new_nodes, expected)

    def test_image_at_start(self):
        node = TextNode(
            "![start](start.jpg) text after",
            TextType.plaintext
        )
        new_nodes = split_nodes_image([node])
        expected = [
            TextNode("start", TextType.image, "start.jpg"),
            TextNode(" text after", TextType.plaintext),
        ]
        self.assertEqual(new_nodes, expected)

    def test_image_at_end(self):
        node = TextNode(
            "text before ![end](end.jpg)",
            TextType.plaintext
        )
        new_nodes = split_nodes_image([node])
        expected = [
            TextNode("text before ", TextType.plaintext),
            TextNode("end", TextType.image, "end.jpg"),
        ]
        self.assertEqual(new_nodes, expected)

    def test_only_image(self):
        node = TextNode(
            "![only](only.jpg)",
            TextType.plaintext
        )
        new_nodes = split_nodes_image([node])
        expected = [
            TextNode("only", TextType.image, "only.jpg"),
        ]
        self.assertEqual(new_nodes, expected)

    def test_no_images(self):
        node = TextNode(
            "Just plain text with no images",
            TextType.plaintext
        )
        new_nodes = split_nodes_image([node])
        expected = [node]  # Should remain unchanged
        self.assertEqual(new_nodes, expected)

    def test_empty_text(self):
        node = TextNode("", TextType.plaintext)
        new_nodes = split_nodes_image([node])
        expected = [node]  # Should remain unchanged
        self.assertEqual(new_nodes, expected)

    def test_non_plaintext_node_unchanged(self):
        node = TextNode("already an image", TextType.image, "img.jpg")
        new_nodes = split_nodes_image([node])
        expected = [node]  # Should remain unchanged
        self.assertEqual(new_nodes, expected)

    def test_multiple_nodes_mixed_types(self):
        nodes = [
            TextNode("First ![img1](url1) text", TextType.plaintext),
            TextNode("Already bold", TextType.bold),
            TextNode("Second ![img2](url2)", TextType.plaintext),
        ]
        new_nodes = split_nodes_image(nodes)
        expected = [
            TextNode("First ", TextType.plaintext),
            TextNode("img1", TextType.image, "url1"),
            TextNode(" text", TextType.plaintext),
            TextNode("Already bold", TextType.bold),
            TextNode("Second ", TextType.plaintext),
            TextNode("img2", TextType.image, "url2"),
        ]
        self.assertEqual(new_nodes, expected)

    def test_consecutive_images(self):
        node = TextNode(
            "![img1](url1)![img2](url2)![img3](url3)",
            TextType.plaintext
        )
        new_nodes = split_nodes_image([node])
        expected = [
            TextNode("img1", TextType.image, "url1"),
            TextNode("img2", TextType.image, "url2"),
            TextNode("img3", TextType.image, "url3"),
        ]
        self.assertEqual(new_nodes, expected)

    def test_image_with_spaces_in_alt(self):
        node = TextNode(
            "![alt text with spaces](https://example.com/image.png)",
            TextType.plaintext
        )
        new_nodes = split_nodes_image([node])
        expected = [
            TextNode("alt text with spaces", TextType.image, "https://example.com/image.png"),
        ]
        self.assertEqual(new_nodes, expected)

    def test_does_not_split_links(self):
        node = TextNode(
            "This is a [link](https://example.com) not an image",
            TextType.plaintext
        )
        new_nodes = split_nodes_image([node])
        expected = [node]  # Should remain unchanged (no images)
        self.assertEqual(new_nodes, expected)

class TestSplitNodesLink(unittest.TestCase):
    def test_single_link(self):
        node = TextNode(
            "This is text with a [link](https://www.example.com)",
            TextType.plaintext
        )
        new_nodes = split_nodes_link([node])
        expected = [
            TextNode("This is text with a ", TextType.plaintext),
            TextNode("link", TextType.link, "https://www.example.com"),
        ]
        self.assertEqual(new_nodes, expected)

    def test_multiple_links(self):
        node = TextNode(
            "[first](https://first.com) and [second](https://second.com)",
            TextType.plaintext
        )
        new_nodes = split_nodes_link([node])
        expected = [
            TextNode("first", TextType.link, "https://first.com"),
            TextNode(" and ", TextType.plaintext),
            TextNode("second", TextType.link, "https://second.com"),
        ]
        self.assertEqual(new_nodes, expected)

    def test_link_at_start(self):
        node = TextNode(
            "[start](start.html) text after",
            TextType.plaintext
        )
        new_nodes = split_nodes_link([node])
        expected = [
            TextNode("start", TextType.link, "start.html"),
            TextNode(" text after", TextType.plaintext),
        ]
        self.assertEqual(new_nodes, expected)

    def test_link_at_end(self):
        node = TextNode(
            "text before [end](end.html)",
            TextType.plaintext
        )
        new_nodes = split_nodes_link([node])
        expected = [
            TextNode("text before ", TextType.plaintext),
            TextNode("end", TextType.link, "end.html"),
        ]
        self.assertEqual(new_nodes, expected)

    def test_only_link(self):
        node = TextNode(
            "[only](only.html)",
            TextType.plaintext
        )
        new_nodes = split_nodes_link([node])
        expected = [
            TextNode("only", TextType.link, "only.html"),
        ]
        self.assertEqual(new_nodes, expected)

    def test_no_links(self):
        node = TextNode(
            "Just plain text with no links",
            TextType.plaintext
        )
        new_nodes = split_nodes_link([node])
        expected = [node]  # Should remain unchanged
        self.assertEqual(new_nodes, expected)

    def test_does_not_split_images(self):
        node = TextNode(
            "This is an ![image](img.jpg) not a link",
            TextType.plaintext
        )
        new_nodes = split_nodes_link([node])
        expected = [node]  # Should remain unchanged (no links due to ! prefix)
        self.assertEqual(new_nodes, expected)

    def test_mixed_images_and_links(self):
        node = TextNode(
            "![image](img.jpg) and [link](page.html) and ![another](img2.png)",
            TextType.plaintext
        )
        new_nodes = split_nodes_link([node])
        # Should only split the link, not the images
        expected = [
            TextNode("![image](img.jpg) and ", TextType.plaintext),
            TextNode("link", TextType.link, "page.html"),
            TextNode(" and ![another](img2.png)", TextType.plaintext),
        ]
        self.assertEqual(new_nodes, expected)

    def test_consecutive_links(self):
        node = TextNode(
            "[link1](url1)[link2](url2)[link3](url3)",
            TextType.plaintext
        )
        new_nodes = split_nodes_link([node])
        expected = [
            TextNode("link1", TextType.link, "url1"),
            TextNode("link2", TextType.link, "url2"),
            TextNode("link3", TextType.link, "url3"),
        ]
        self.assertEqual(new_nodes, expected)

    def test_link_with_spaces_in_text(self):
        node = TextNode(
            "[link text with spaces](https://example.com)",
            TextType.plaintext
        )
        new_nodes = split_nodes_link([node])
        expected = [
            TextNode("link text with spaces", TextType.link, "https://example.com"),
        ]
        self.assertEqual(new_nodes, expected)

    def test_relative_urls(self):
        node = TextNode(
            "[about](/about) [contact](./contact.html)",
            TextType.plaintext
        )
        new_nodes = split_nodes_link([node])
        expected = [
            TextNode("about", TextType.link, "/about"),
            TextNode(" ", TextType.plaintext),
            TextNode("contact", TextType.link, "./contact.html"),
        ]
        self.assertEqual(new_nodes, expected)

    def test_multiple_nodes_mixed_types_links(self):
        nodes = [
            TextNode("First [link1](url1) text", TextType.plaintext),
            TextNode("Already italic", TextType.italic),
            TextNode("Second [link2](url2)", TextType.plaintext),
        ]
        new_nodes = split_nodes_link(nodes)
        expected = [
            TextNode("First ", TextType.plaintext),
            TextNode("link1", TextType.link, "url1"),
            TextNode(" text", TextType.plaintext),
            TextNode("Already italic", TextType.italic),
            TextNode("Second ", TextType.plaintext),
            TextNode("link2", TextType.link, "url2"),
        ]
        self.assertEqual(new_nodes, expected)

    def test_empty_text_link(self):
        node = TextNode("", TextType.plaintext)
        new_nodes = split_nodes_link([node])
        expected = [node]  # Should remain unchanged
        self.assertEqual(new_nodes, expected)

    def test_non_plaintext_node_unchanged_link(self):
        node = TextNode("already a link", TextType.link, "url")
        new_nodes = split_nodes_link([node])
        expected = [node]  # Should remain unchanged
        self.assertEqual(new_nodes, expected)

class TestTextToTextNodes(unittest.TestCase):
    def test_plain_text_only(self):
        text = "Just plain text without any formatting"
        nodes = text_to_textnodes(text)
        expected = [TextNode("Just plain text without any formatting", TextType.plaintext)]
        self.assertEqual(nodes, expected)

    def test_bold_only(self):
        text = "This is **bold text** in a sentence"
        nodes = text_to_textnodes(text)
        expected = [
            TextNode("This is ", TextType.plaintext),
            TextNode("bold text", TextType.bold),
            TextNode(" in a sentence", TextType.plaintext),
        ]
        self.assertEqual(nodes, expected)

    def test_italic_only(self):
        text = "This is *italic text* in a sentence"
        nodes = text_to_textnodes(text)
        expected = [
            TextNode("This is ", TextType.plaintext),
            TextNode("italic text", TextType.italic),
            TextNode(" in a sentence", TextType.plaintext),
        ]
        self.assertEqual(nodes, expected)

    def test_code_only(self):
        text = "This is `code text` in a sentence"
        nodes = text_to_textnodes(text)
        expected = [
            TextNode("This is ", TextType.plaintext),
            TextNode("code text", TextType.codetext),
            TextNode(" in a sentence", TextType.plaintext),
        ]
        self.assertEqual(nodes, expected)

    def test_image_only(self):
        text = "This is an ![image](https://example.com/img.jpg) in text"
        nodes = text_to_textnodes(text)
        expected = [
            TextNode("This is an ", TextType.plaintext),
            TextNode("image", TextType.image, "https://example.com/img.jpg"),
            TextNode(" in text", TextType.plaintext),
        ]
        self.assertEqual(nodes, expected)

    def test_link_only(self):
        text = "This is a [link](https://example.com) in text"
        nodes = text_to_textnodes(text)
        expected = [
            TextNode("This is a ", TextType.plaintext),
            TextNode("link", TextType.link, "https://example.com"),
            TextNode(" in text", TextType.plaintext),
        ]
        self.assertEqual(nodes, expected)

    def test_multiple_bold(self):
        text = "**First bold** and **second bold**"
        nodes = text_to_textnodes(text)
        expected = [
            TextNode("First bold", TextType.bold),
            TextNode(" and ", TextType.plaintext),
            TextNode("second bold", TextType.bold),
        ]
        self.assertEqual(nodes, expected)

    def test_multiple_italic(self):
        text = "*First italic* and *second italic*"
        nodes = text_to_textnodes(text)
        expected = [
            TextNode("First italic", TextType.italic),
            TextNode(" and ", TextType.plaintext),
            TextNode("second italic", TextType.italic),
        ]
        self.assertEqual(nodes, expected)

    def test_bold_and_italic_together(self):
        text = "**Bold** and *italic* in same sentence"
        nodes = text_to_textnodes(text)
        expected = [
            TextNode("Bold", TextType.bold),
            TextNode(" and ", TextType.plaintext),
            TextNode("italic", TextType.italic),
            TextNode(" in same sentence", TextType.plaintext),
        ]
        self.assertEqual(nodes, expected)

    def test_bold_with_italic_adjacent(self):
        text = "**Bold***Italic*"
        nodes = text_to_textnodes(text)
        expected = [
            TextNode("Bold", TextType.bold),
            TextNode("Italic", TextType.italic),
        ]
        self.assertEqual(nodes, expected)

    def test_image_and_link_together(self):
        text = "![image](img.jpg) and [link](page.html)"
        nodes = text_to_textnodes(text)
        expected = [
            TextNode("image", TextType.image, "img.jpg"),
            TextNode(" and ", TextType.plaintext),
            TextNode("link", TextType.link, "page.html"),
        ]
        self.assertEqual(nodes, expected)

    def test_code_with_formatting_around(self):
        text = "Text with `code` and **bold**"
        nodes = text_to_textnodes(text)
        expected = [
            TextNode("Text with ", TextType.plaintext),
            TextNode("code", TextType.codetext),
            TextNode(" and ", TextType.plaintext),
            TextNode("bold", TextType.bold),
        ]
        self.assertEqual(nodes, expected)

    def test_complex_combination(self):
        text = "This is **bold**, *italic*, `code`, ![image](img.jpg), and [link](url)"
        nodes = text_to_textnodes(text)
        expected = [
            TextNode("This is ", TextType.plaintext),
            TextNode("bold", TextType.bold),
            TextNode(", ", TextType.plaintext),
            TextNode("italic", TextType.italic),
            TextNode(", ", TextType.plaintext),
            TextNode("code", TextType.codetext),
            TextNode(", ", TextType.plaintext),
            TextNode("image", TextType.image, "img.jpg"),
            TextNode(", and ", TextType.plaintext),
            TextNode("link", TextType.link, "url"),
        ]
        self.assertEqual(nodes, expected)

    def test_empty_string(self):
        text = ""
        nodes = text_to_textnodes(text)
        expected = [TextNode("", TextType.plaintext)]
        self.assertEqual(nodes, expected)

    def test_only_formatting(self):
        text = "**bold**"
        nodes = text_to_textnodes(text)
        expected = [TextNode("bold", TextType.bold)]
        self.assertEqual(nodes, expected)

    def test_formatting_at_start(self):
        text = "**bold** at start"
        nodes = text_to_textnodes(text)
        expected = [
            TextNode("bold", TextType.bold),
            TextNode(" at start", TextType.plaintext),
        ]
        self.assertEqual(nodes, expected)

    def test_formatting_at_end(self):
        text = "text at end **bold**"
        nodes = text_to_textnodes(text)
        expected = [
            TextNode("text at end ", TextType.plaintext),
            TextNode("bold", TextType.bold),
        ]
        self.assertEqual(nodes, expected)

    def test_multiple_consecutive_formatting(self):
        text = "**bold****more bold**"
        nodes = text_to_textnodes(text)
        expected = [
            TextNode("bold", TextType.bold),
            TextNode("more bold", TextType.bold),
        ]
        self.assertEqual(nodes, expected)

    def test_link_not_mistaken_for_image(self):
        text = "This is [a link](page.html) not ![an image](img.jpg)"
        nodes = text_to_textnodes(text)
        expected = [
            TextNode("This is ", TextType.plaintext),
            TextNode("a link", TextType.link, "page.html"),
            TextNode(" not ", TextType.plaintext),
            TextNode("an image", TextType.image, "img.jpg"),
        ]
        self.assertEqual(nodes, expected)

    def test_image_not_mistaken_for_link(self):
        text = "This is ![an image](img.jpg) not [a link](page.html)"
        nodes = text_to_textnodes(text)
        expected = [
            TextNode("This is ", TextType.plaintext),
            TextNode("an image", TextType.image, "img.jpg"),
            TextNode(" not ", TextType.plaintext),
            TextNode("a link", TextType.link, "page.html"),
        ]
        self.assertEqual(nodes, expected)

    def test_special_characters_in_text(self):
        text = "Text with & special <chars> **bold**"
        nodes = text_to_textnodes(text)
        expected = [
            TextNode("Text with & special <chars> ", TextType.plaintext),
            TextNode("bold", TextType.bold),
        ]
        self.assertEqual(nodes, expected)

    def test_unicode_characters(self):
        text = "Text with 🚀 **rocket** and 😊 **smile**"
        nodes = text_to_textnodes(text)
        expected = [
            TextNode("Text with 🚀 ", TextType.plaintext),
            TextNode("rocket", TextType.bold),
            TextNode(" and 😊 ", TextType.plaintext),
            TextNode("smile", TextType.bold),
        ]
        self.assertEqual(nodes, expected)

    def test_code_preserves_content(self):
        # Code should preserve asterisks and brackets literally
        text = "This is `**not bold**` and `![not image]`"
        nodes = text_to_textnodes(text)
        expected = [
            TextNode("This is ", TextType.plaintext),
            TextNode("**not bold**", TextType.codetext),
            TextNode(" and ", TextType.plaintext),
            TextNode("![not image]", TextType.codetext),
        ]
        self.assertEqual(nodes, expected)

    def test_does_not_process_formatting_in_code(self):
        # What's inside code blocks should not be processed
        text = "`**code with stars**` and **actual bold**"
        nodes = text_to_textnodes(text)
        expected = [
            TextNode("**code with stars**", TextType.codetext),
            TextNode(" and ", TextType.plaintext),
            TextNode("actual bold", TextType.bold),
        ]
        self.assertEqual(nodes, expected)

    def test_does_not_process_links_in_code(self):
        text = "`[not a link]` and [actual link](url)"
        nodes = text_to_textnodes(text)
        expected = [
            TextNode("[not a link]", TextType.codetext),
            TextNode(" and ", TextType.plaintext),
            TextNode("actual link", TextType.link, "url"),
        ]
        self.assertEqual(nodes, expected)


    def test_bold_at_very_beginning(self):
        text = "**bold**text"
        nodes = text_to_textnodes(text)
        expected = [
            TextNode("bold", TextType.bold),
            TextNode("text", TextType.plaintext),
        ]
        self.assertEqual(nodes, expected)

    def test_bold_at_very_end(self):
        text = "text**bold**"
        nodes = text_to_textnodes(text)
        expected = [
            TextNode("text", TextType.plaintext),
            TextNode("bold", TextType.bold),
        ]
        self.assertEqual(nodes, expected)

    def test_link_with_formatting_in_text(self):
        # Test case that might be problematic: [**bold link**](url)
        # Most markdown parsers don't process formatting inside link text
        text = "[**bold link**](url)"
        nodes = text_to_textnodes(text)
        # Should be a link with text "**bold link**"
        expected = [TextNode("**bold link**", TextType.link, "url")]
        self.assertEqual(nodes, expected)
    

if __name__ == "__main__":
    unittest.main()

    """ the link and image extractor cant capture nested brackets or parentheses in urls, or links with title atributes,
    but it works for the basic cases needed for now. """