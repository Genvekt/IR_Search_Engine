Feature: Load Documents

  Scenario: Load Document
    Given Document url
    When Load it from memory or download
    Then Load is successful