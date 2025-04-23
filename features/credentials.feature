Feature: Credential Management

  Scenario: Issue and Accept a Credential Offer
    Given the system has initialized with user and credential configurations
    When the user requests credential schemas
    And retrieves the offering link for the user over NATS
    And creates a cryptographic key pair
    Then the system creates a credential offer based on the issued credential
    When the user accepts the created offer
    Then the new credential is stored in the user's wallet

  Scenario: Issuance offer with 2-Factor Auth
    Given the system has initialized with user and credential configurations
    When the user requests credential schemas
    And retrieves the offering link for the user over NATS with 2-Factor Auth
    And creates a cryptographic key pair
    Then the system creates a credential offer based on the issued credential

  Scenario: Present credential
    Given services are running
    When the user receives a presentation request
    Then user sends the presentation to the verifier
    And the presentation is saved

  Scenario: Issue, then Revoke and Accept revoked a Credential Offer
    Given the system has initialized with user and credential configurations
    When the user requests credential schemas
    And retrieves the offering link for the user over NATS
    And creates a cryptographic key pair
    Then the system creates a credential offer based on the issued credential
    When the user accepts the created offer
    And the user revokes the created credential
    Then verification of credential fails

  Scenario: 2-Factor Auth
    Given the system has initialized with user and credential configurations
    When the user requests credential schemas
    And creates a cryptographic key pair
    And subscription to the 2-Factor Pin topic is created
    And retrieves the offering link for the user over NATS with 2-Factor Auth
    Then subscription to the 2-Factor Pin topic is activated
    And the system creates a credential offer based on the issued credential
    When the user accepts the created offer
    Then the new credential is stored in the user's wallet