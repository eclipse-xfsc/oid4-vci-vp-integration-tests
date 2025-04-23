from src.eu.xfsc.bdd.ocm_w.components import Didcomm
from src.eu.xfsc.bdd.ocm_w.components.context import DIDCOMM_SERVICE_URL, TENANT, DIDCOMM_SERVICE_EXTERNAL_URL
from src.eu.xfsc.bdd.ocm_w.utils import cleanup_nats


def before_all(context):
    context.userId = None
    context.offeringData = None
    context.credentialOfferSubject = None
    context.searchValue = None
    context.offeringId = None
    context.credentialType = None
    context.presentation_id = None


def after_scenario(context, scenario):
    if scenario.feature.name == "Didcomconnector":
        if getattr(context, "from_did", None) is not None:
            resp = Didcomm(DIDCOMM_SERVICE_URL, TENANT).delete_connection(context.from_did)
            if not resp.ok:
                print(f"{scenario.feature.name} Cleanup: Failed to delete connection with DID {context.from_did}")
            else:
                print(f"{scenario.feature.name} Cleanup: Deleted connection with DID {context.from_did}")

            resp = Didcomm(DIDCOMM_SERVICE_EXTERNAL_URL, TENANT).delete_connection(context.from_did)
            if not resp.ok:
                print(f"{scenario.feature.name} Cleanup: Failed to delete connection with DID {context.from_did}")
            else:
                print(f"{scenario.feature.name} Cleanup: Deleted connection with DID {context.from_did}")


    cleanup_nats(
            nats_clients=getattr(context, "nats_clients", None),
            futures=getattr(context, "futures", None),
            subscriptions=getattr(context, "subscriptions", None),
            loop=getattr(context, "a_loop", None)
        )