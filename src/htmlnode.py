class HtmlNode:
    def __init__(self, tag = None, value = None, children = None, props = None):
        self.tag = tag
        self.value = value
        self.children = children 
        self.props = props 
    def to_html(self):
        raise NotImplementedError("to_html method not implemented")
    def props_to_html(self):
        if not self.props:
            return ""
        props_str = ""
        for key, value in self.props.items():
            props_str += f' {key}="{value}"'
        return props_str
    def __repr__(self):
        return f"HtmlNode(tag={self.tag}, value={self.value}, children={self.children}, props={self.props})"

    
    

class LeafNode(HtmlNode):
    def __init__(self, tag = None, value = None, props = None):
        super().__init__(tag=tag, value=value, children=None, props=props)

    def to_html(self):
        if self.value is None:
              raise ValueError("Leaf nodes must have a value")
        if self.tag is None:
              return str(self.value)
        props_str = self.props_to_html()
        return f"<{self.tag}{props_str}>{self.value}</{self.tag}>"

    

class ParentNode(HtmlNode):
    def __init__(self, tag = None, children = None, props = None):
        super().__init__(tag=tag, value=None, children=children, props=props)

    def to_html(self):
        if self.tag is None:
            raise ValueError("Parent nodes must have a tag")
        if self.children is None:
            raise ValueError("Parent nodes must have children")
        props_str = self.props_to_html()
        children_html = "".join(child.to_html() for child in self.children) if self.children else ""
        return f"<{self.tag}{props_str}>{children_html}</{self.tag}>"