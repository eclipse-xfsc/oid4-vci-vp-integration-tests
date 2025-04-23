from time import sleep
from urllib.parse import urlparse, parse_qs

import requests
from behave import use_step_matcher, given, when, then, step

from src.eu.xfsc.bdd.ocm_w.components import Presentation, ProofModel, FilterResult, Signer, Storage
from src.eu.xfsc.bdd.ocm_w.components.context import SIGNER_SERVICE_URL, NATS_URL, PRESENTATION_SERVICE_URL, TENANT, NATS_HEALTH_URL, ContextType, USER_ID, STORAGE_SERVICE_URL, UNIQUE_CRED_SUBJECT, USER_CRYPTO_KEY_ID, USER_CRYPTO_KEY_NAMESPACE

use_step_matcher("re")


@given("services are running")
def check_running(context: ContextType) -> None:
    """
    :type context: behave.runner.Context
    """
    assert Presentation(PRESENTATION_SERVICE_URL, TENANT).is_healthy()
    assert Storage(STORAGE_SERVICE_URL, TENANT).is_healthy()
    assert Signer(SIGNER_SERVICE_URL, TENANT, NATS_URL).is_healthy()
    assert requests.get(f"{NATS_HEALTH_URL}/varz").ok


@when("the user receives a presentation request")
def receive_presentation_request(context: ContextType):
    """
    :param context:
    :return:
    """
    pres_service = Presentation(PRESENTATION_SERVICE_URL, TENANT)
    # request url would be received externally
    request_url = pres_service.get_authorize_request_url(UNIQUE_CRED_SUBJECT, "www.holder-wallet.com")
    response = pres_service.authorize_presentation(request_url, USER_ID, 700000)
    assert response.status_code == 302, f"response was received with content {response.content.decode()}"
    tmp = response.headers.get("Location")
    assert tmp
    redirect_url = urlparse(tmp)
    query_params = parse_qs(redirect_url.query)
    assert "presentation" in query_params, f"presentation request was not received {query_params}"
    context.presentation_id = query_params["presentation"][0]


@then("user sends the presentation to the verifier")
def create_presentation_for_request(context):
    """
    :type context: behave.runner.Context
    """
    pres_service = Presentation(PRESENTATION_SERVICE_URL, TENANT)
    response = pres_service.get_presentation_request(context.presentation_id)
    assert response.ok, f"response from {response.url} was received with content {response.content.decode()}"
    data = response.json()
    # Credential verification service creates 2 data entries. Both should be assigned to the user
    response_assign = pres_service.assign_presentation_request(USER_ID, context.presentation_id)
    assert response_assign.ok, f"response from {response_assign.url}  for id was received with content {response_assign.content.decode()}"
    response_assign = pres_service.assign_presentation_request(USER_ID, data["requestId"])
    assert response_assign.ok, f"response from {response_assign.url} for requestId was received with content {response_assign.content.decode()}"

    # Validate the presentation definition returned
    assert "presentationDefinition" in data, f"presentation definition was not received {data}"
    pres_def = data["presentationDefinition"]
    assert "input_descriptors" in pres_def, f"presentation definition was not received {pres_def}"
    assert "constraints" in pres_def["input_descriptors"][0], f"presentation definition was not received {pres_def}"
    assert "fields" in pres_def["input_descriptors"][0]["constraints"], f"presentation definition was not received {pres_def}"
    assert "path" in pres_def["input_descriptors"][0]["constraints"]["fields"][0], f"presentation definition was not received {pres_def}"
    assert "filter" in pres_def["input_descriptors"][0]["constraints"]["fields"][0], f"presentation definition was not received {pres_def}"
    assert "pattern" in pres_def["input_descriptors"][0]["constraints"]["fields"][0]["filter"], f"presentation definition was not received {pres_def}"
    assert pres_def["input_descriptors"][0]["constraints"]["fields"][0]["filter"]["pattern"] == UNIQUE_CRED_SUBJECT, f"presentation definition was not received {pres_def}"

    # Retrieve credentials that will be included in the presentation
    cred_resp = Storage(STORAGE_SERVICE_URL, TENANT).get_credentials(USER_ID, UNIQUE_CRED_SUBJECT)
    assert cred_resp.ok, f"response from {cred_resp.url} was received with content {cred_resp.content.decode()}"
    cred_data = cred_resp.json()
    assert "groups" in cred_data, f"credentials were not received {cred_data}"
    assert len(cred_data["groups"]) > 0, f"credentials were not received {cred_data}"

    # Remove proof from credentials as proof is not passing credential structure validation during signing
    Storage(STORAGE_SERVICE_URL, TENANT).drop_proofs(cred_data)

    # Fetch did used for signing
    resp = Signer(SIGNER_SERVICE_URL, TENANT, NATS_URL).get_dids(USER_ID, USER_CRYPTO_KEY_NAMESPACE)
    assert resp.ok, f"response from {resp.url} was received with content {resp.content.decode()}"
    data = resp.json().get("list", [])
    assert len(data) > 0, f"keys were not received {data}"

    # send presentation
    payload=[FilterResult(**item) for item in cred_data["groups"]]
    for item in payload:
        item.description["format"] = "ldp_vp"
    response_pres = pres_service.save_presentation(context.presentation_id,
                                                   ProofModel(payload=payload,
                                                              signNamespace=USER_CRYPTO_KEY_NAMESPACE,
                                                              signKey=data[0]["name"],
                                                              signGroup=USER_ID,
                                                              holderDid=data[0]["did"]
                                                              )
                                                   )
    assert response_pres.ok, f"response from {response_pres.url} was received with content {response_pres.content.decode()}"


@step("the presentation is saved")
def check_new_presentation(context: ContextType):
    """
    :type context: behave.runner.Context
    """
    sleep(5) # for storage service to have time to save new presentation, as presentation is passed to storage service asynchronously using broker
    response = Storage(STORAGE_SERVICE_URL, TENANT).get_presentations(USER_ID)
    assert response.ok, response.status_code + " "+ response.content
    data = response.json().get("groups", [])
    assert len(data) > 0, f"get presentation result {response.content}"
    assert "credentials" in data[0]
    credentials = data[0]["credentials"]
    assert len(credentials) > 0
