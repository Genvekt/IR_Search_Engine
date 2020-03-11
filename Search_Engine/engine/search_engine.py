from time import sleep

from pymongo import MongoClient
from utils.config import CRAWLER_RATE, DUMP_RATE

from engine.index.database_handler import DatabaseHandler
import threading
from engine.crawler import Crawler
from engine.index.inverted_index import InvertedIndex
from engine.document.song import Song
from engine.index.prefix_tree import PrefixTree
from engine.index.soundex_index import Soundex
from engine.searcher.query_handler import QueryHandler


class SearchEngine:
    def __init__(self, db: MongoClient):
        self.collection = {}
        self.pref_tree = PrefixTree()
        self.soundex = Soundex()
        self.inverted_index = InvertedIndex()
        self.DBH = DatabaseHandler()
        self.QH = QueryHandler(inverted_index=self.inverted_index,
                               soundex=self.soundex,
                               prefix_tree=self.pref_tree,
                               DBH=self.DBH)

        self.songs_list = []
        self.background_event = threading.Event()
        self.crawler = None

    def collect_documents(self, source: str, amount: int, event: threading.Event):
        id = self.DBH.get_songs_number() + 1
        crawler = Crawler()
        self.collection = {}
        previous_indexer = None
        for c in crawler.crawl_generator(source, amount):
            if not c.doc.author + c.doc.title in self.songs_list:
                sleep(CRAWLER_RATE)
                # Structure final song class
                new_song = Song(id=id, author=c.doc.author, title=c.doc.title,
                                text=c.doc.text, url=c.doc.url)
                # Pass the song to indexing thread
                print('Saving song', id)
                current_indexer = threading.Thread(target=self.index_document,
                                                   args=(new_song, previous_indexer, event))
                current_indexer.start()
                # Remember the indexer
                previous_indexer = current_indexer
                id += 1

    def index_document(self, new_song: Song, previous_indexer: threading.Thread, event: threading.Event):
        # Wait the previous indexer to finish the task
        print('Indexer waits for previous to finish....')
        if previous_indexer:
            previous_indexer.join()
        # Close critical region
        if event.is_set():
            print('Indexer waits for region...')
            event.wait()
        event.set()
        print('Indexer start work')
        # Save new song and update the index
        self.collection[new_song.id] = new_song
        self.update_index(song=new_song)
        if len(self.collection) > DUMP_RATE:
            # Dump the data to disk if there is enough songs to store
            self.save()
        event.clear()
        print('Indexer finished')

    def init_index(self):
        self.inverted_index.from_collection(list[self.collection.values()])
        self.soundex.from_collection(list[self.collection.values()])
        self.pref_tree.from_collection(list[self.collection.values()])

    def update_index(self, song: Song):
        self.inverted_index.from_collection([song])
        self.soundex.from_collection([song])
        self.pref_tree.from_collection([song])

    def resolve_query(self, query: str):
        if self.background_event.is_set():
            self.background_event.wait()
        self.background_event.set()

        self.QH.parse(query)
        doc_ids = self.QH.execute()
        matched_documents = []
        docs_from_db = []
        for doc_id in doc_ids:
            if not doc_id in self.collection.keys():
                docs_from_db.append(doc_id)
            else:
                matched_documents.append([self.collection[doc_id], doc_id, 'RAM'])
        print('Found docs in database: ', docs_from_db)
        print('Found docs in ram: ', matched_documents)

        db_songs = self.DBH.get_documents(docs_from_db)

        self.background_event.clear()

        for s in db_songs:
            matched_documents.append([s, s.id, 'DB'])
        return matched_documents

    def save(self):
        # Save inverted index
        print("To save:", len(self.collection))
        self.DBH.dump_inverted_index(self.inverted_index.index)

        # Save soundex
        # self.DBH.dump_soundex(self.soundex.index)

        # Save Prefix Tree
        # self.DBH.dump_prefix_tree(self.pref_tree.root)

        # Save Collection
        self.DBH.dump_collection([v for k, v in self.collection.items()])

        self.clear()
        print("Saved!")

    def load(self):
        """
        Constract prefix tree and soundex from db documents
        """
        self.pref_tree = PrefixTree()
        self.soundex = Soundex()
        self.songs_list = self.DBH.song_list()
        song_ids = self.DBH.id_list()
        for id in song_ids:
            songs = self.DBH.get_documents([id])
            self.pref_tree.from_collection(songs)
            self.soundex.from_collection(songs)
        self.QH = QueryHandler(inverted_index=self.inverted_index,
                               soundex=self.soundex,
                               prefix_tree=self.pref_tree,
                               DBH=self.DBH)

    def clear(self):
        self.collection = {}
        # self.pref_tree = PrefixTree()
        # self.soundex = Soundex()
        self.inverted_index = InvertedIndex()
        self.QH = QueryHandler(inverted_index=self.inverted_index,
                               soundex=self.soundex,
                               prefix_tree=self.pref_tree,
                               DBH=self.DBH)

    def start_crawler(self):
        if not self.crawler:
            self.crawler = threading.Thread(target=self.collect_documents,
                                            args=("https://www.lyrics.com/", 20, self.background_event))

            self.crawler.start()
