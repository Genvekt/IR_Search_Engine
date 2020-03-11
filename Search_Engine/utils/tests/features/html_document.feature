Feature: Parse html document

  Scenario: Parse html with song
    Given Document url
    When Load document and parse content
    Then Parse is successful