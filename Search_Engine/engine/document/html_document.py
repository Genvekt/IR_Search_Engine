from bs4 import BeautifulSoup
from engine.document.document import Document
import urllib.parse


class HtmlDocumentTextData:

    def __init__(self, url):
        self.doc = HtmlDocument(url)
        self.doc.get()
        self.doc.parse()


class HtmlDocument(Document):
    def parse(self):
        # Create parser and plase for parsed data

        parser = BeautifulSoup(self.content, 'html')
        self.anchors = []
        self.text = []
        self.author = ''
        self.title = ''

        # Get all (text,href) pairs from <a> tags
        for item in parser.find_all('a', href=True, text=True):
            url_field = urllib.parse.urljoin(self.url, item['href'])
            if url_field[:23] == "https://www.lyrics.com/":
                self.anchors.append((item.text, url_field))

        # Get author name if exists
        author = parser.find_all('h3', {'class': 'lyric-artist'})
        if not author == []:
            if author[0].a:
                self.author = author[0].a.text
            else:
                self.author = author[0].text

        # Get song title if exists
        title = parser.find_all('h2', id="lyric-title-text")
        if not title:
            title = parser.find_all('h1', id="lyric-title-text")
        if not title == []:
            if title[0].a:
                self.title = title[0].a.text
            else:
                self.title = title[0].text

        # Get the text of song if exiists
        texts = parser.find_all('pre', id="lyric-body-text")

        self.text = u" ".join(t.text.strip() for t in texts if t != '')
