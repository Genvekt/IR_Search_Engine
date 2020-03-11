from engine.index.soundex_index import Soundex
import pytest
from pytest_bdd import given, when, then, scenarios

scenarios('./features/soundex.feature')


def run_test():
    pass


@given('Strings')
def get_words():
    return ['Ashcraft', 'implementation', 'Rubin']


@pytest.fixture
@when('Each word is converted to soundex')
def convert(get_words):
    sex = Soundex()
    words = get_words
    codes = [sex.word_to_soundex(word) for word in words]
    return codes


@then('Code is correct')
def check_document(convert):
    codes = convert
    assert codes[0] == 'A261'
    assert codes[1] == 'I514'
    assert codes[2] == 'R150'
