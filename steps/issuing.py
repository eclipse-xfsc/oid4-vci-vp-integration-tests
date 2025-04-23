import requests

from time import sleep

from behave import use_step_matcher, given, when, then, step

from src.eu.xfsc.bdd.ocm_w.components import WellKnown, DummyIssuer, CredentialRetrieval, Storage, Signer, StatusList
from src.eu.xfsc.bdd.ocm_w.components.context import STATUS_LIST_SERVICE_URL, SIGNER_SERVICE_URL, WELL_KNOWN_SERVICE_URL, CREDENTIAL_RETRIEVAL_SERVICE_URL, STORAGE_SERVICE_URL, DUMMY_ISSUER_URL, TENANT, NATS_URL, ISSUER_TOPIC, USER_ID, USER_CRYPTO_KEY_ID, USER_CRYPTO_KEY_NAMESPACE, NATS_HEALTH_URL, ContextType, UNIQUE_CRED_SUBJECT

use_step_matcher("re")


@given("the system has initialized with user and credential configurations")  # type: ignore
def services_bootstrapped(context: ContextType) -> None:
    """
    :type context: behave.runner.Context
    """
    assert WellKnown(WELL_KNOWN_SERVICE_URL, TENANT).is_healthy()
    assert CredentialRetrieval(CREDENTIAL_RETRIEVAL_SERVICE_URL, TENANT).is_healthy()
    assert Storage(STORAGE_SERVICE_URL, TENANT).is_healthy()
    assert Signer(SIGNER_SERVICE_URL, TENANT, NATS_URL).is_healthy()
    assert requests.get(f"{NATS_HEALTH_URL}/varz").ok


@when("the user requests credential schemas")  # type: ignore
def request_schemas(context: ContextType) -> None:
    """
    :type context: behave.runner.Context
    """
    response = WellKnown(WELL_KNOWN_SERVICE_URL, TENANT).get_schemas()
    assert response.ok, f"response status {response.status_code}"
    data = response.json()
    assert "credential_configurations_supported" in data, "metadata structure"
    assert "DeveloperCredential" in data["credential_configurations_supported"], "metadata structure"
    context.credentialType = "DeveloperCredential"
    schema = data["credential_configurations_supported"][context.credentialType]
    assert "credential_definition" in schema, "metadata structure"
    definition = schema["credential_definition"]
    assert "credentialSubject" in definition, "metadata structure"
    context.searchValue = UNIQUE_CRED_SUBJECT
    context.credentialOfferSubject = {key: UNIQUE_CRED_SUBJECT for key in definition.get("credentialSubject", {}).keys()}


@step("retrieves the offering link for the user over NATS")  # type: ignore
def get_offering(context: ContextType) -> None:
    """
    :type context: behave.runner.Context
    """
    offering = DummyIssuer(DUMMY_ISSUER_URL, TENANT, NATS_URL, ISSUER_TOPIC).get_offering(context.credentialType, context.credentialOfferSubject)
    assert not offering.get("error"), f"offering error {offering.get('error')}"
    assert "offer" in offering
    offer_data = offering.get("offer")
    assert "credential_offer" in offer_data, "offer object structure"
    offer = offer_data["credential_offer"]
    assert offer.startswith("openid-credential-offer://"), "valid offering link"
    context.offeringData = offer_data


@step("retrieves the offering link for the user over NATS with 2-Factor Auth")  # type: ignore
def get_offering(context: ContextType) -> None:
    """
    :type context: behave.runner.Context
    """
    offering = DummyIssuer(DUMMY_ISSUER_URL, TENANT, NATS_URL, ISSUER_TOPIC).get_offering(context.credentialType, context.credentialOfferSubject, two_factor=True)
    assert not offering.get("error"), f"offering error {offering.get('error')}"
    assert "offer" in offering
    offer_data = offering.get("offer")
    assert "credential_offer" in offer_data, "offer object structure"
    offer = offer_data["credential_offer"]
    assert offer.startswith("openid-credential-offer://"), "valid offering link"
    context.offeringData = offer_data


@then("the system creates a credential offer based on the issued credential")  # type: ignore
def create_offering(context: ContextType) -> None:
    """
    :type context: behave.runner.Context
    """
    response = CredentialRetrieval(CREDENTIAL_RETRIEVAL_SERVICE_URL, TENANT).offer(USER_ID, context.offeringData)
    assert response.ok, f"offer creation status {response.status_code} and result result {response.content}"
    offering_id = response.json()
    context.offeringId = offering_id


@when("the user accepts the created offer")  # type: ignore
def accept_offer_twofactor(context: ContextType) -> None:
    """
    :type context: behave.runner.Context
    """
    response = CredentialRetrieval(CREDENTIAL_RETRIEVAL_SERVICE_URL, TENANT).clear(USER_ID, context.offeringId, True, USER_CRYPTO_KEY_ID, USER_CRYPTO_KEY_NAMESPACE, getattr(context, "tx_code", ""))
    assert response.ok, f"offer acceptance status {response.status_code} and result result {response.content}"


@then("the new credential is stored in the user's wallet")  # type: ignore
def get_new_credential(context: ContextType) -> None:
    """
    :type context: behave.runner.Context
    """
    sleep(5)
    get_credentials()


def get_credentials():
    response = Storage(STORAGE_SERVICE_URL, TENANT).get_credentials(USER_ID, UNIQUE_CRED_SUBJECT)
    assert response.ok, f"get credentials status {response.status_code} and result result {response.content}"
    data = response.json()
    # Storage(STORAGE_SERVICE_URL, TENANT).drop_proofs(data)
    data = data.get("groups", [])
    assert len(data) > 0
    assert "credentials" in data[0]
    credentials = data[0]["credentials"]
    assert len(credentials) >= 1, f"expected >=1 credential, got {len(credentials)}"
    return list(credentials.values())[0]


@step("creates a cryptographic key pair")  # type: ignore
def create_key(context: ContextType) -> None:
    """
    :type context: behave.runner.Context
    """
    res = Signer("", TENANT, NATS_URL).create_key(USER_ID, "ecdsa-p256", USER_CRYPTO_KEY_ID, USER_CRYPTO_KEY_NAMESPACE)
    assert not res.get("error")


@step("the user revokes the created credential")
def revoke_credential(context):
    """
    :type context: behave.runner.Context
    """
    sleep(5)
    credential = get_credentials()
    cred_status = credential["credentialStatus"]
    print(cred_status)
    lcr = cred_status["statusListCredential"]
    print(lcr)
    list_id = lcr.split("/status/")[-1]
    list_index = cred_status["statusListIndex"]
    print(f"list_id={list_id}, list_index={list_index}")
    response = StatusList(STATUS_LIST_SERVICE_URL, TENANT).revoke_credential(list_id, list_index)
    assert response.ok, f"revoke credential status {response.status_code} and result {response.content}"
    context.revoked_credential = credential


@then("verification of credential fails")
def verify_credential_fails(context):
    """
    :type context: behave.runner.Context
    """
    response = Signer(SIGNER_SERVICE_URL, TENANT, NATS_URL).verify_credential(USER_ID, USER_CRYPTO_KEY_NAMESPACE, context.revoked_credential)
    assert response.ok, response.text
    assert not response.json().get("valid", True)
