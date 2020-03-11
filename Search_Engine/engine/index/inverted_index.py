from typing import List

from engine.document.song import Song


class InvertedIndex:
    def __init__(self):
        self.index = {}

    def from_collection(self, collection: List[Song]):
        for song in collection:
            # Process song text
            words = song.get_word_stats(lemmatization=True, without_stop_words=True)
            for word in words:
                if not word in self.index.keys():
                    self.index[word] = []
                self.index[word].append(song.id)
    