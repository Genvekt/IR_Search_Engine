import requests
from pathlib import Path
from utils.config import APP_ROOT


class Document:
    RESOURCE_DIR = Path(APP_ROOT) / 'resources/docs'

    def __init__(self, url):
        self.url = url
        self.content = b''

    def get(self):
        if not self.load():
            if not self.download():
                raise FileNotFoundError(self.url)
            else:
                self.persist()

    def download(self):
        # Try to connect to the url
        try:
            r = requests.get(self.url, allow_redirects=True)
        # Catch badly formatted urls
        except requests.exceptions.InvalidSchema:
            return False
        # Catch non responding urls
        except requests.exceptions.RequestException:
            return False
        # Get content
        self.content = r.content
        return True

    def persist(self):
        # Create filename from url
        if '/' in self.url:
            filename = self.url.replace('/', '_')
        else:
            filename = self.url
        file_path = self.RESOURCE_DIR / filename
        # Save file
        open(file_path, 'wb').write(self.content)

    def load(self):
        # Create filename from url
        if '/' in self.url:
            filename = self.url.replace('/', '_')
        else:
            filename = self.url
        # Try to open file
        try:
            file_path = self.RESOURCE_DIR / filename
            f = open(file_path, 'rb')
            self.content = f.read()
            f.close()
        # Catch files that does not exist
        except IOError:
            return False
        return True
