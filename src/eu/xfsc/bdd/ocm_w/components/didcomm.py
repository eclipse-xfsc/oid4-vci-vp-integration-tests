import base64
import json
import uuid
from typing import Any

import requests

from .component import Service


class Didcomm(Service):

    def __init__(self, url: str, tenant: str):
        super().__init__(url, tenant)

    def create_invitation(self, protocol: str, topic: str, event_type: str, group: str, payload: dict[str, str]) -> requests.Response:
        url = f"{self.url}/admin/invitation"
        data = {
            "Protocol": protocol,
            "Topic": topic,
            "EventType": event_type,
            "Properties": payload,
            "Group": group
        }
        return requests.post(url, json=data, verify=False)

    def is_healthy(self) -> bool:
        url = f"{self.url}/health"
        res = requests.get(url)
        return res.ok

    def accept_invitation(self, invitation: str, protocol: str, topic: str, event_type: str, group: str, payload: dict[str, Any] = {}) -> requests.Response:
        url = f"{self.url}/admin/connections/accept"
        data = {
            "Protocol": protocol,
            "Topic": topic,
            "EventType": event_type,
            "Properties": payload,
            "Group": group,
            "Invitation": invitation
        }
        return requests.post(url, json=data, verify=False)

    def delete_connection(self, connection_did: str) -> requests.Response:
        url = f"{self.url}/admin/connections/{connection_did}"
        return requests.delete(url, verify=False, timeout=5)

    def block_connection(self, connection_did: str) -> requests.Response:
        url = f"{self.url}/admin/connections/block/{connection_did}"
        return requests.post(url, verify=False)

    def unblock_connection(self, connection_did: str) -> requests.Response:
        url = f"{self.url}/admin/connections/unblock/{connection_did}"
        return requests.post(url, verify=False)

    def is_blocked(self, connection_did: str) -> requests.Response:
        url = f"{self.url}/admin/connections/isblocked/{connection_did}"
        return requests.get(url, verify=False)

    def receive_event(self, from_did: str, to_did: str, payload: dict[str, str], did_id: str = "did:test:123") -> requests.Response:
        url = f"{self.url}/message/receive"
        data = {
            "id": str(uuid.uuid4()),
            "type": "https://didcomm.org/routing/2.0/forward",
            "body": {
                "next": to_did
            },
            "from": did_id,
            "to": [
                from_did
            ],
            "attachments": [
                {
                    "id": "test",
                    "data": {
                        "base64": base64.b64encode(json.dumps(payload).encode()).decode("utf-8")
                    }
                }
            ]
        }
        return requests.post(url, json=data, verify=False)
