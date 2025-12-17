from textnode import TextNode, TextType
def main():
    node1 = TextNode("This is some anchor text", TextType.link, "https://www.boot.dev")
    node2 = TextNode("This is some anchor text", TextType.link, "https://www.boot.dev")
    print(f"node1: {node1}")
    print(f"node1.text: {node1.text}")
    print(f"node1.text_type: {node1.text_type}")
    print(f"node1.url: {node1.url}")

    node3 = TextNode("Goodbye World", TextType.italic, None)
    print(f"node3: {node3}")
    print(f"node1 == node2: {node1 == node2}")
    print(f"node1 == node3: {node1 == node3}")
    
main()