Feature: Didcomconnector

  Scenario: Create and delete connection
    Given the system is up
    Then user creates an offering DIDcomm invitation
    Then subscription to the internal messaging topic is created
    And user accepts the invitation
    And subscription to the internal messaging topic is activated
    Then deletes a created connection

  Scenario: Send event over DIDcomm
    Given the system is up
    When the user requests credential schemas
    And retrieves the offering link for the user over NATS
    Then user creates an offering DIDcomm invitation
    Then subscription to the internal messaging topic is created
    And user accepts the invitation
    And subscription to the internal messaging topic is activated
    Then subscription to the offering topic is created
    And user sends a routing request to DIDcomm
    And subscription to the offering topic is activated
    Then deletes a created connection

  Scenario: Forwarding via blocked connection
    Given the system is up
    Then user creates an offering DIDcomm invitation
    And user accepts the invitation
    Then the connection is blocked
    And connection status is blocked
    Then the connection is unblocked
    And connection status is not blocked
    Then deletes a created connection