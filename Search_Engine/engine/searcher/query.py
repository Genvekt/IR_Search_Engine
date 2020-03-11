from pymongo import MongoClient

from engine.index.database_handler import DatabaseHandler
from engine.index.inverted_index import InvertedIndex


class Query:

    def __init__(self, query_type='AND'):
        if query_type in ['AND', 'OR']:
            self.query_type = query_type
            self.items = []
        else:
            raise ValueError()

    def add_subquery(self, query):
        '''
        Add another query to the items
        '''
        self.items.append([query, 'q'])

    def add_one_item(self, item):
        '''
        Add simple item to the items
        '''
        self.items.append([item, 't'])

    def add_all(self, items):
        '''
        Add all items from array
        '''
        self.items.extend([[item, 't'] for item in items])

    def execute(self, inverted_index: InvertedIndex, DBH: DatabaseHandler):
        '''
        Translate items to corresponding docs and apply query parameter
        '''
        found_docs = []
        for item in self.items:
            if item[1] == 't':
                relevant_docs = set()
                if item[0] in inverted_index.index.keys():
                    for d in inverted_index.index[item[0]]:
                        relevant_docs.add(d)
                if DBH.word_exists_in_index(item[0]):
                    for d in DBH.get_docs_by_word(item[0]):
                        relevant_docs.add(d)
                found_docs.append(list(relevant_docs))
            else:
                found_docs.append(item[0].execute(inverted_index, DBH))

        if self.query_type == 'AND':
            return self.apply_AND(found_docs)
        else:
            return self.apply_OR(found_docs)

    def apply_AND(self, array):
        '''
        Find intersection
        '''
        if array == []:
            return []

        # Find array with minimal length
        min_index = 0
        min_len = 100000000
        for i in range(len(array)):
            if len(array[i]) < min_len:
                min_index = i

        # Sort numbers from that array that appears in all other arrays
        result = []
        for doc_id in array[min_index]:
            found_times = 0
            for i in range(len(array)):
                if doc_id in array[i]:
                    found_times += 1
            if found_times == len(array):
                result.append(doc_id)
        return (result)

    def apply_OR(self, array):
        '''
        Find union
        '''
        result = set()
        for docs in array:
            for doc in docs:
                result.add(doc)
        return list(result)

    def show(self, intend):
        print(intend, self.query_type)
        for item in self.items:
            if item[1] == 't':
                print(intend, '-', item[0])
            else:
                print(intend, '- Subquery:')
                item[0].show(intend + '\t')
