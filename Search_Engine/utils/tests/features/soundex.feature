Feature: Coundex encoding

  Scenario: Word to soundex
    Given Strings
    When Each word is converted to soundex
    Then Code is correct