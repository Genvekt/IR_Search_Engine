import pytest
from pytest_bdd import given, when, then, scenarios
from engine.document.html_document import HtmlDocument

scenarios('./features/html_document.feature')


def run_test():
    pass

@given('Document url')
def get_url():
    return "https://www.lyrics.com/lyric/36380389/Billie+Eilish/Bad+Guy"

@pytest.fixture
@when('Load document and parse content')
def load_document(get_url):
    doc = HtmlDocument(get_url)
    doc.get()
    doc.parse()
    return doc

@then('Parse is successful')
def check_document(load_document):
    doc = load_document
    assert "Like it really rough guy" in doc.text, "Error parsing song text"
    assert "bad guy" == doc.title, "Error parsing song title"
    assert "Billie Eilish" == doc.author, "Error parsing song author"
    assert any(p[1] == "https://www.lyrics.com/lyric/36380389/Billie+Eilish/artist/Billie-Eilish/3177510"
               for p in doc.anchors), "Error parsing links"