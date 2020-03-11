Feature: Parse song from html document

  Scenario: Parse song
    Given Song url
    When Load document and parse song
    Then Parse is successful