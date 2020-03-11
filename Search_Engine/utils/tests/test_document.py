import pytest
from pytest_bdd import given, when, then, scenarios
from engine.document.document import Document

scenarios('./features/document.feature')


def run_test():
    pass

@given('Document url')
def get_url():
    return 'http://sprotasov.ru/data/iu.txt'

@pytest.fixture
@when('Load it from memory or download')
def load_document(get_url):
    doc = Document(get_url)
    doc.get()
    return doc

@then('Load is successful')
def check_document(load_document):
    doc = load_document
    assert doc.content, "Document download failed"
    assert "Code snippets, demos and labs for the course" in str(doc.content), "Document content error"
    assert doc.load(), "Load should return true for saved document"
    assert "Code snippets, demos and labs for the course" in str(doc.content), "Document load from disk error"