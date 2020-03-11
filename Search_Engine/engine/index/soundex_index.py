import re
from typing import List

from engine.document.song import Song


class Soundex:
    soundex_codes = {
        'b': '1', 'f': '1', 'p': '1', 'v': '1',
        'c': '2', 'g': '2', 'j': '2', 'k': '2',
        'q': '2', 's': '2', 'x': '2', 'z': '2',
        'd': '3', 't': '3',
        'l': '4',
        'm': '5', 'n': '5',
        'r': '6'
    }

    def __init__(self):
        self.index = {}

    def word_to_soundex(self, word):

        if word == '':
            return ''
        # 1
        first_letter = word[0].upper()
        # 2
        word_without_h_w = re.sub(r"[wh]", '', word[1:])
        # 3
        word_with_numbers = word_without_h_w
        for char in self.soundex_codes.keys():
            word_with_numbers = re.sub(r"[" + char + "]", self.soundex_codes[char], word_with_numbers)
        # 4
        word_shrinked = re.sub(r'(\w)\1{1,}', r'\1', word_with_numbers)
        # 5
        word_cleared = re.sub(r'[aiouey]', '', word_shrinked)
        # 6
        word_to_cut = first_letter + word_cleared
        if len(word_to_cut) < 4:
            word_to_cut += '0' * (4 - len(word_to_cut))
        # 7
        return word_to_cut[:4]

    def from_collection(self, collection: List[Song]):
        for c in collection:
            # Process song text
            words = c.get_word_stats(lemmatization=False, without_stop_words=False)
            for word in words:
                code = self.word_to_soundex(word)
                if not code in self.index.keys():
                    self.index[code] = set()
                self.index[code].add(word)
