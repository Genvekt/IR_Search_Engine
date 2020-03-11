from queue import Queue
from engine.document.html_document import HtmlDocumentTextData


class Crawler:

    def __init__(self):
        self.queue = Queue()
        self.root = ''
        self.limit = 0
        self.visited = []
        self.collected = 0

    def restart(self, source: str, max_docs_num: int):
        self.queue = Queue()
        self.root = source
        self.limit = max_docs_num
        self.queue.put(self.root)
        self.visited = []
        self.collected = 0

    def is_visited(self, url):
        if url in self.visited:
            return True
        else:
            return False

    def is_bad_url(self, url):
        if url[-4:] in ('.pdf', '.mp3', '.avi', '.mp4', '.txt', '.php'):
            return True
        else:
            return False

    def mark_visited(self, item):
        self.visited.append(item)

    def put_in_queue(self, item):
        self.queue.put(item)

    def get_next_url(self):
        return self.queue.get()

    def crawl_generator(self, source, max_docs_num):

        # Restart parameters
        self.restart(source, max_docs_num)
        while self.collected < self.limit and not self.queue.empty():

            # Fetch url from queue
            url = self.get_next_url()

            # Make sure it was not visited yet and not leads to file
            if self.is_visited(url) or self.is_bad_url(url):
                continue

            # Try to connect 3 times
            for i in range(3):
                try:
                    data = HtmlDocumentTextData(url)
                    # Exit loop on success
                    break
                except FileNotFoundError:
                    # If it is the third failure, mark as visited and proceed
                    if i == 2:
                        self.mark_visited(url)
                        continue

            # Remember contained urls
            for child in data.doc.anchors:
                self.put_in_queue(child[1])

            # Mark url as visited
            self.mark_visited(url)

            # Check if it is a song page
            if data.doc.text == '':
                # Not song
                continue
            else:
                # Remember song name - title pair
                song = data.doc.author + data.doc.title
                # Check if song has already been saved
                if self.is_visited(song):
                    continue
                self.mark_visited(song)

                self.collected += 1
                print(self.collected, ": ", data.doc.author, " - ", data.doc.title)
                print(url)
            yield data
