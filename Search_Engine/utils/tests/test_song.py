import pytest
from pytest_bdd import given, when, then, scenarios
from engine.document.html_document import HtmlDocumentTextData
from engine.document.song import Song

scenarios('./features/song.feature')


def run_test():
    pass

@given('Song url')
def get_url():
    return "https://www.lyrics.com/lyric/36380389/Billie+Eilish/Bad+Guy"

@pytest.fixture
@when('Load document and parse song')
def load_song(get_url):
    d = HtmlDocumentTextData(get_url)
    s = Song(0, d.doc.author, d.doc.title, d.doc.text, 'https://www.lyrics.com/lyric/36380389/Billie+Eilish/Bad+Guy')
    return s

@then('Parse is successful')
def check_document(load_song):
    s = load_song
    assert "Like it really rough guy" in s.text, "Error parsing song text"
    assert "bad guy" == s.title, "Error parsing song title"
    assert "Billie Eilish" == s.author, "Error parsing song author"