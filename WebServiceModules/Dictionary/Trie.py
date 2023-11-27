class TrieNode:
    def __init__(self):
        self.children = {}
        self.is_end = False
        self.value = None


def add_to_trie(root, words, value):
    node = root
    for word in words:
        if word not in node.children:
            node.children[word] = TrieNode()
        node = node.children[word]
    node.is_end = True
    node.value = value


def find_in_trie(root, words):
    node = root
    for word in words:
        if word not in node.children:
            return False, None
        node = node.children[word]
    return node.is_end, node.value

