from typing import List
from utils.config import LEAF_NODE

from pymongo import MongoClient

from engine.document.song import Song


class DatabaseHandler:
    def __init__(self):
        self.db = MongoClient('localhost', 27017).search_engine
        self.prefix_tree = self.db.prefix_tree
        self.songs = self.db.songs
        self.soundex = self.db.soundex
        self.inverted_index = self.db.inverted_index

    def word_exists_in_prefix_tree(self, word: str):
        found = self.prefix_tree.find_one({"_id": word + LEAF_NODE})
        if found:
            return True
        return False

    def word_exists_in_index(self, word: str):
        found = self.inverted_index.find_one({"_id": word})
        if found:
            return True
        return False

    def find_all(self, prefix: str) -> [str]:
        found = self.prefix_tree.find_one({"_id": prefix})
        if not found:
            return []
        found_words = []
        for larger_prefix in found['children']:
            if larger_prefix[-1] == LEAF_NODE:
                found_words.append(prefix)
            else:
                found_words.extend(self.find_all(larger_prefix))
        return found_words

    def get_words_by_code(self, code: str):
        found = self.soundex.find_one({"_id": code})
        if found:
            return found["words"]
        else:
            return []

    def get_docs_by_word(self, word: str):
        found = self.inverted_index.find_one({"_id": word})
        if found:
            return found["documents"]
        else:
            return []

    def get_documents(self, doc_ids: List[int]) -> List[Song]:
        found_songs = []
        for doc_id in doc_ids:
            d = self.songs.find_one({"_id": doc_id})
            found_songs.append(Song(d["_id"], d["author"], d["title"], d["text"], d["url"]))
        return found_songs

    def song_list(self):
        songs = [doc["author"] + doc["title"] for doc in self.songs.find({}, {'author': 1 , 'title': 1})]
        return songs

    def id_list(self):
        songs = [doc["_id"] for doc in self.songs.find({}, {'_id': 1})]
        return songs

    def get_songs_number(self):
        return self.songs.count()

    def get_song(self, id: int):
        d = self.songs.find_one({"_id": id})
        print(d)
        if not d:
            return None
        else:
            return Song(d["_id"], d["author"], d["title"], d["text"], d["url"])

    def dump_collection(self, songs: List[Song]):
        for song in songs:
            print(song.id)
            self.songs.insert({
                "_id": song.id,
                "author": song.author,
                "title": song.title,
                "text": song.text,
                "url": song.url
            })

    def dump_inverted_index(self, inverted_index: dict):
        for word, docs in inverted_index.items():
            # try to find out if word already un undex
            found = self.inverted_index.find_one({"_id": word})
            if not found:
                self.inverted_index.insert({"_id": word, "documents": docs})
            else:
                for doc_id in docs:
                    self.inverted_index.update({"_id": word}, {'$push': {"documents": doc_id}})

    def dump_soundex(self, soundex: dict):
        for code, words in soundex.items():
            found = self.soundex.find_one({"_id": code})
            if not found:
                self.soundex.insert({"_id": code, "words": list(words)})
            else:
                old_words = set(found["words"])
                for word in words:
                    old_words.add(word)
                self.soundex.update({"_id": code}, {'$set': {"words": list(old_words)}})

    def dump_prefix_tree(self, prefix_tree: dict, node_id=''):
        # Extract the node from db
        node = self.prefix_tree.find_one({"_id": node_id})
        # Create node if it does not exists
        if not node:
            self.prefix_tree.insert_one({"_id": node_id, "children": []})
            node = self.prefix_tree.find_one({"_id": node_id})
        children = node["children"]
        update_children = False
        for child, subtree in prefix_tree.items():
            # Check if child is in children
            child_id = node_id + child
            if not child_id in children:
                children.append(child_id)
                update_children = True

            self.dump_prefix_tree(prefix_tree=subtree, node_id=child_id)

        if update_children:
            self.prefix_tree.update({"_id": node_id}, {'$set': {"children": children}})
