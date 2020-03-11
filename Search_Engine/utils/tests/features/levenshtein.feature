Feature: Levenshtein distance

  Scenario: Calculate levenshtein distance
    Given Two words
    When Levenshtein distance is computed
    Then Distance is correct