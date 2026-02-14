class Node:
    def __init__(self, kind, value=None, children=None):
        self.kind = kind
        self.value = value
        self.children = children or []

    def __repr__(self):
        if self.children:
            return f"Node(kind={self.kind}, value={self.value}, children={self.children})"
        return f"Node(kind={self.kind}, value={self.value})"
