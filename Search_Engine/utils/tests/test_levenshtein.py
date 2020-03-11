from utils.levenshtein import levenshtein

import pytest
from pytest_bdd import given, when, then, scenarios

scenarios('./features/levenshtein.feature')


def run_test():
    pass


@given('Two words')
def get_words():
    return 'aa', 'ann'


@pytest.fixture
@when('Levenshtein distance is computed')
def calculate_distance(get_words):
    word1, word2 = get_words
    return levenshtein(word1, word2)


@then('Distance is correct')
def check_distance(calculate_distance):
    dist = calculate_distance
    assert dist == 2
