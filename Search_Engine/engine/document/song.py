from utils.text_processing import preprocess
from collections import Counter
from engine.document.html_document import HtmlDocumentTextData


class Song:
    def __init__(self,id, author='', title='', text='', url=''):
        self.id = id
        self.author = author
        self.title = title
        self.text = text
        self.url = url

    def from_url(self, url: str):
        data = HtmlDocumentTextData(url)
        self.url = url
        self.author = data.doc.author
        self.title = data.doc.title
        self.text = data.doc.text

    def get_words(self, lemmatization=True, without_stop=True):
        return preprocess(self.text, lemmatize=lemmatization, without_stop_words=without_stop)

    def get_word_stats(self, lemmatization=True, without_stop_words=True):
        return Counter(self.get_words(lemmatization, without_stop_words))
