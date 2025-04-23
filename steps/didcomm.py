import base64
import json
from time import sleep
from typing import Awaitable

import asyncio
import requests
from urllib.parse import urlparse, parse_qs

from behave import use_step_matcher, given, when, then, step

from src.eu.xfsc.bdd.ocm_w.components import WellKnown, DummyIssuer, CredentialRetrieval, Storage, Signer, StatusList, Didcomm
from src.eu.xfsc.bdd.ocm_w.components.context import NATS_URL_EXTERNAL, DIDCOMM_SERVICE_EXTERNAL_URL, STATUS_LIST_SERVICE_URL, SIGNER_SERVICE_URL, WELL_KNOWN_SERVICE_URL, CREDENTIAL_RETRIEVAL_SERVICE_URL, STORAGE_SERVICE_URL, DUMMY_ISSUER_URL, TENANT, NATS_URL, ISSUER_TOPIC, USER_ID, USER_CRYPTO_KEY_ID, USER_CRYPTO_KEY_NAMESPACE, NATS_HEALTH_URL, ContextType, UNIQUE_CRED_SUBJECT, DIDCOMM_SERVICE_URL

from nats.aio.client import Subscription, Client as NATS
from nats.aio.msg import Msg

from eu.xfsc.bdd.ocm_w.utils import base64_padding

use_step_matcher("re")

OFFERING_CREATE_TOPIC = "offering"
OFFERING_CREATE_EVENT_TYPE = "retrieval.offering.external"
DIDCOMM_INTERNAL_TOPIC = "/message/receive-invitation"
TWO_FACTOR_PIN_TOPIC = "two-factor.pin"


def test_async_nats_subscription_triggered(topic: str, nats_url: str, loop: asyncio.AbstractEventLoop, nc: NATS) -> asyncio.Future[Msg]:
    message_future = loop.create_future()
    # subscription_lock = asyncio.Lock()
    async def callback(msg: Msg) -> None:
        nonlocal message_future
        if not message_future.done():
            print(f"Received message: {msg}")
            message_future.set_result(msg)


    async def func() -> tuple[Awaitable, Subscription]:
        nonlocal message_future
        await nc.connect(nats_url)
        print(f"Subscribing to topic {topic}")
        # async with subscription_lock:
        sub = await nc.subscribe(topic, max_msgs=1, cb=callback)
        return asyncio.wait_for(message_future, timeout=20), sub
        # return message_future, sub


    return loop.run_until_complete(func())


@given("the system is up")  # type: ignore
def system_is_up(context: ContextType) -> None:
    assert Didcomm(DIDCOMM_SERVICE_URL, TENANT).is_healthy()


@then("user creates an offering DIDcomm invitation")
def create_invitation(context: ContextType) -> None:
    response = (Didcomm(DIDCOMM_SERVICE_URL, TENANT).create_invitation(
        protocol="nats",
        topic=OFFERING_CREATE_TOPIC,
        group="test",
        event_type=OFFERING_CREATE_EVENT_TYPE,
        payload=context.offeringData or {"credential_offer":"test"}))

    assert response.ok, f"create_invitation response status {response.status_code}"
    data, inv = process_invitation(response)
    print(data)
    context.from_did = data["from"]
    context.auth = data["body"]["auth"]
    context.didcomm_invitation = inv


def process_invitation(response: requests.Response) -> tuple[dict[str, str], str]:
    inv = response.content.decode("utf-8")
    url = urlparse(inv)
    query_params = parse_qs(url.query)
    assert "_oob" in query_params, f"oob not in queryParams {query_params}"
    oob = query_params["_oob"][0]
    oob = base64_padding(oob)
    data = json.loads(base64.b64decode(oob, validate=True).decode("utf-8"))
    assert "from" in data, f"`from` not in data {data}"
    assert "body" in data, f"body not in data {data}"
    assert "auth" in data["body"], f"auth not in data {data}"
    return data, inv


@then("subscription to the internal messaging topic is created")
def subscribe_to_topic_internal(context: ContextType) -> None:
    nc = NATS()
    if not getattr(context, "a_loop", None):
        loop = asyncio.new_event_loop()
        loop.set_debug(True)
        context.a_loop = loop
    if not getattr(context, "nats_clients", None):
        context.nats_clients = {}

    future, sub = test_async_nats_subscription_triggered(DIDCOMM_INTERNAL_TOPIC, NATS_URL, context.a_loop, nc)

    if not getattr(context, "futures", None):
        context.futures = {}
    if not getattr(context, "subscriptions", None):
        context.subscriptions = {}

    context.nats_clients[DIDCOMM_INTERNAL_TOPIC] = nc
    context.futures[DIDCOMM_INTERNAL_TOPIC] = future
    context.subscriptions[DIDCOMM_INTERNAL_TOPIC] = sub


@then("user accepts the invitation")
def accept_invitation(context: ContextType) -> None:
    response = Didcomm(DIDCOMM_SERVICE_EXTERNAL_URL, TENANT).accept_invitation(
        context.didcomm_invitation,
        protocol="nats",
        topic=OFFERING_CREATE_TOPIC,
        group="test",
        event_type=OFFERING_CREATE_EVENT_TYPE,
        payload={"credential_offer":"test"}
    )

    assert response.ok, f"accept_invitation response status {response.status_code} content {response.content}"
    to_did = response.content.decode("utf-8")
    if to_did.startswith('"'):
        to_did = to_did[1:]
    if to_did.endswith('"'):
        to_did = to_did[:-1]
    context.to_did = to_did


@step("subscription to the internal messaging topic is activated")
def check_subscription_internal(context: ContextType) -> None:
    if context.futures.get(DIDCOMM_INTERNAL_TOPIC, None):
        received_message = context.a_loop.run_until_complete(context.futures[DIDCOMM_INTERNAL_TOPIC])
        assert received_message is not None, "Subscription was activated but no message was received"
    else:
        assert False, "No subscription might have been activated"


@then("deletes a created connection")
def delete_connection(context: ContextType) -> None:
    response = Didcomm(DIDCOMM_SERVICE_URL, TENANT).delete_connection(context.from_did)
    assert response.ok, f"delete_connection response status {response.status_code} content {response.content}"
    context.from_did = None


@then("subscription to the offering topic is created")
def subscribe_to_topic_offering(context: ContextType) -> None:
    nc = NATS()
    if not getattr(context, "a_loop", None):
        loop = asyncio.new_event_loop()
        loop.set_debug(True)
        context.a_loop = loop
    if not getattr(context, "nats_clients", None):
        context.nats_clients = {}

    future, sub = test_async_nats_subscription_triggered(OFFERING_CREATE_TOPIC, NATS_URL, context.a_loop, nc)

    if not getattr(context, "futures", None):
        context.futures = {}
    if not getattr(context, "subscriptions", None):
        context.subscriptions = {}
    context.futures[OFFERING_CREATE_TOPIC] = future
    context.subscriptions[OFFERING_CREATE_TOPIC] = sub
    context.nats_clients[OFFERING_CREATE_TOPIC] = nc


@when("subscription to the 2-Factor Pin topic is created")
def subscribe_to_topic_2factor(context: ContextType) -> None:
    nc = NATS()
    if not getattr(context, "a_loop", None):
        loop = asyncio.new_event_loop()
        loop.set_debug(True)
        context.a_loop = loop
    if not getattr(context, "nats_clients", None):
        context.nats_clients = {}

    future, sub = test_async_nats_subscription_triggered(TWO_FACTOR_PIN_TOPIC, NATS_URL, context.a_loop, nc)
    if not getattr(context, "futures", None):
        context.futures = {}
    if not getattr(context, "subscriptions", None):
        context.subscriptions = {}
    context.futures[TWO_FACTOR_PIN_TOPIC] = future
    context.subscriptions[TWO_FACTOR_PIN_TOPIC] = sub
    context.nats_clients[TWO_FACTOR_PIN_TOPIC] = nc


@then("subscription to the 2-Factor Pin topic is activated")
def check_subscription_2factor(context: ContextType) -> None:
    sleep(5)
    if context.futures.get(TWO_FACTOR_PIN_TOPIC, None):
        received_message = context.a_loop.run_until_complete(context.futures[TWO_FACTOR_PIN_TOPIC])
        assert received_message is not None, "Subscription was activated but no message was received"
        context.tx_code = json.loads(received_message.data.decode("utf-8"))["data"]["body"]
    else:
        assert False, "No subscription might have been activated"



@then("user sends a routing request to DIDcomm")
def receive_event(context: ContextType) -> None:
    response = Didcomm(DIDCOMM_SERVICE_URL, TENANT).receive_event(from_did=context.from_did, to_did=context.to_did, payload={})
    assert response.ok, f"receive_event response status {response.status_code} content {response.content}"


@then("subscription to the offering topic is activated")
def check_subscription_offering(context: ContextType) -> None:
    sleep(5)
    if context.futures.get(OFFERING_CREATE_TOPIC, None):
        received_message = context.a_loop.run_until_complete(context.futures[OFFERING_CREATE_TOPIC])
        assert received_message is not None, "Subscription was activated but no message was received"
    else:
        assert False, "No subscription might have been activated"


@then("the connection is blocked")
def block_connection(context):
    """
    :type context: behave.runner.Context
    """
    response = Didcomm(DIDCOMM_SERVICE_URL, TENANT).block_connection(context.from_did)
    assert response.ok, f"block_connection response status {response.status_code} content {response.content}"



@then("the connection is unblocked")
def unblock_connection(context):
    """
    :type context: behave.runner.Context
    """
    response = Didcomm(DIDCOMM_SERVICE_URL, TENANT).unblock_connection(context.from_did)
    assert response.ok, f"unblock_connection response status {response.status_code} content {response.content}"


@step("connection status is blocked")
def is_blocked_true(context):
    """
    :type context: behave.runner.Context
    """
    response = Didcomm(DIDCOMM_SERVICE_URL, TENANT).is_blocked(context.from_did)
    assert response.ok, f"is_blocked response status {response.status_code} content {response.content}"
    assert response.json(), f"Connection status is not blocked"


@step("connection status is not blocked")
def is_blocked_false(context):
    """
    :type context: behave.runner.Context
    """
    response = Didcomm(DIDCOMM_SERVICE_URL, TENANT).is_blocked(context.from_did)
    assert response.ok, f"is_blocked response status {response.status_code} content {response.content}"
    assert not response.json(), f"Connection status is not blocked"

