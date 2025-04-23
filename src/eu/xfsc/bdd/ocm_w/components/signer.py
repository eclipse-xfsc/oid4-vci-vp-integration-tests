import base64
import uuid

import json
from pynats import NATSClient
from cloudevents.http import CloudEvent
from cloudevents.conversion import to_dict
import requests


from .component import Service

SIGNER_TOPIC = "signer-topic"

CREATE_KEY_TYPE = "signer.createKey"


class Signer(Service):  # type: ignore
    def __init__(self, url: str, tenant: str, nats_url: str):
        super().__init__(url, tenant)
        self.nats_url = nats_url

    def create_key(self, user_id: str, key_type: str, key_name: str, key_namespace: str) -> dict[str, str]:
        with NATSClient(url=self.nats_url) as client:
            client.connect()
            req = dict(tenant_id=self.tenant, request_id=str(uuid.uuid4()), group=user_id, type=key_type, key=key_name, namespace=key_namespace)
            attrs = {"type": CREATE_KEY_TYPE, "source": "bdd_test", "contenttype": "application/json"}
            event = CloudEvent(attributes=attrs, data=req)
            data = to_dict(event)
            reply = client.request(SIGNER_TOPIC, payload=json.dumps(data).encode("utf-8"))
            print(reply)
            return json.loads(reply.payload).get("data", {})

    def get_dids(self, user_id: str, namespace: str) -> requests.Response:
        url = f"{self.url}/v1/did/list"
        headers = {
            "x-namespace": namespace,
            "x-group": user_id
        }
        return requests.get(url, headers=headers, verify=False)

    def verify_credential(self, user_id: str, namespace: str, credential: dict[str, str]) -> requests.Response:
        url = f"{self.url}/v1/credential/verify"
        headers = {
            "x-namespace": namespace,
            "x-group": user_id
        }
        cred_str = json.dumps(credential)
        print(f"Verify credential {cred_str}")
        cred_data = base64.b64encode(cred_str.encode("utf-8"))
        payload = {"credential": cred_data.decode()}
        payload_serialised = json.dumps(payload)
        print(f"Verify credential payload {payload_serialised}")
        return requests.post(url, headers=headers, data=payload_serialised, verify=False)

    def is_healthy(self) -> bool:
        url = f"{self.url}/readiness"
        res = requests.get(url)
        return res.ok
