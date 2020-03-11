from engine.index.database_handler import DatabaseHandler
from engine.index.inverted_index import InvertedIndex
from engine.index.prefix_tree import PrefixTree
from engine.index.soundex_index import Soundex
from engine.searcher.query import Query
from pymongo import MongoClient
from utils.text_processing import preprocess, lemmatization, remove_stop_words
from utils.levenshtein import levenshtein
from utils.config import WORD_END


class QueryHandler:
    def __init__(self, inverted_index: InvertedIndex, soundex: Soundex,
                 prefix_tree: PrefixTree, DBH: DatabaseHandler):
        self.inverted_index = inverted_index
        self.soundex = soundex
        self.pt = prefix_tree
        self.query = Query('AND')
        self.DBH = DBH

    def parse(self, text):
        self.query = Query('AND')

        def symbol_to_end(string, symbol, cut_symbol=False):
            '''
            aaaSaaa -> aaaaaaS where S is special symbol
            '''
            index = string.find(symbol)
            return string[index + 1:] + string[:index]

        # Preprocess without lemmatization
        tokens = preprocess(text, lemmatize=False, without_stop_words=True)
        for token in tokens:
            print("Analysing: ", token)

            # If * in word
            if '*' in token:
                # Find all matches and add to OR subquery
                token = token + WORD_END
                token = symbol_to_end(token, '*')
                words = self.pt.find_all(token)
                #words.extend(self.DBH.find_all(token))
                words = [symbol_to_end(word, WORD_END) for word in words]
                print("\t* found. Possible matches: ", words)
                subquery = Query('OR')
                for word in lemmatization(words):
                    subquery.add_one_item(word)
                self.query.add_subquery(subquery)

            # If word exists in inverted undex
            elif self.pt.find_word(token + WORD_END): # or self.DBH.word_exists_in_prefix_tree(token + WORD_END):
                print("\t Regular word.")
                # Add to maim AND query
                self.query.add_one_item(token)

            # If word does not exists in inverted undex
            else:
                # Find words with same soudex code
                print("\tFound tipo: ", token)
                token_code = self.soundex.word_to_soundex(token)

                similar_words = [] #[[word, levenshtein(word, token)] for word in self.DBH.get_words_by_code(token_code)]
                if token_code in self.soundex.index.keys() :
                    similar_words.extend([[word, levenshtein(word, token)] for word in list(self.soundex.index[token_code])])
                if len(similar_words) > 0:
                    print("\tTrying to replace with: ", similar_words)
                    # Find the closest by levenshtain distance
                    min_dist = min(similar_words, key=lambda x: x[1])[1]
                    close_words = [item[0] for item in similar_words if item[1] == min_dist]
                else:
                    close_words = []
                print("\tBest fit found: ", close_words)

                # If there is stop words in variands, skip query
                close_without_stop = remove_stop_words(close_words)
                if len(close_without_stop) < len(close_words):
                    print("\tStop word found in variants, skipping.")
                    continue

                # If there is no stop words, add closest words to OR subquery
                else:
                    subquery = Query('OR')
                    subquery.add_all(lemmatization(close_words))
                    self.query.add_subquery(subquery)

    def execute(self):
        '''
        Find the docid matching given query
        '''
        self.show()
        return self.query.execute(self.inverted_index, self.DBH)

    def show(self):
        self.query.show('')
