from utils.config import WORD_END, LEAF_NODE

class PrefixTree:
    def __init__(self):
        self.root = {}
        self.leaf_key = LEAF_NODE

    def _insert_word(self, word):
        '''
        Add a single word to the tree
        '''
        i = 0  # Current char in word
        last_node = self.root  # Found node where prefix ends

        # Find on whish node prefix ends
        while i < len(word) and word[i] in last_node.keys():
            last_node = last_node[word[i]]
            i += 1

        # If there still chars to add
        while i < len(word):
            new_node = {}
            last_node[word[i]] = new_node
            last_node = last_node[word[i]]
            i += 1

        # Add links to documents
        last_node[self.leaf_key] = {}

    def _find_prefix(self, word):
        '''
        Find the node on which prefix ends
        '''
        i = 0  # Current char in word
        last_node = self.root  # Found node where prefix ends

        # Find the last reachable node
        while i < len(word) and word[i] in last_node.keys():
            last_node = last_node[word[i]]
            i += 1

        # If there are no more chars, node is found
        if i >= len(word):
            return last_node

        # If there are more chars, prefix does not exists
        else:
            return {}

    def find_word(self, word):
        '''
        Search if word is present in the tree
        '''
        last_node = self._find_prefix(word)
        if self.leaf_key in last_node.keys():
            return True
        else:
            return False

    def find_all(self, prefix):
        '''
        Find all words that start with this prefix
        '''
        last_node = self._find_prefix(prefix)
        return self.dfs(last_node, prefix)

    def dfs(self, node, prefix):
        '''
        Traverse for all words starting from specific node
        '''
        if node == {}:
            return []
        else:
            found = []
            for k in node.keys():
                if k == self.leaf_key:
                    found.append(prefix)
                else:
                    found.extend(self.dfs(node[k], prefix + k))
            return found

    def add(self, word):
        '''
        Add word and all its permutations
        '''
        words = self.permute(word)
        for w in words:
            self._insert_word(w)

    def permute(self, word):
        '''
        Create all possible permutations from the word
        '''
        permutations = []
        for i in range(len(word)):
            word = word[1:] + word[:1]
            permutations.append(word)
        return permutations


    def from_collection(self, collection):
        for c in collection:
            # Process song text
            words = c.get_word_stats(lemmatization=False, without_stop_words=False)
            for word in words:
                self.add(word + WORD_END)
