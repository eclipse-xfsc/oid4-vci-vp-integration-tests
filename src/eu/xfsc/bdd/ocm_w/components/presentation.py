import base64
from urllib.parse import quote

import requests
import uuid
import json

from .component import Service


from dataclasses import dataclass, asdict
from typing import List, Any


@dataclass
class FilterResult:
    # Assuming the structure of presentation.FilterResult includes an id and other fields
    # Adjust the fields according to the actual structure
    # id: str
    # name: str
    # purpose: str
    # format: str
    description: dict[str, str]
    credentials: dict[str, Any]


@dataclass
class ProofModel:
    payload: List[FilterResult]
    signNamespace: str
    signKey: str
    signGroup: str
    holderDid: str


class Presentation(Service):  # type: ignore
    def __init__(self, url: str, tenant: str):
        super().__init__(url, tenant)

    def get_presentation_request(self, presentation_id: str) -> requests.Response:
        url = f"{self.url}/v1/tenants/{self.tenant}/internal/proofs/proof/{presentation_id}"
        headers = {
            "Content-Type": "application/json"
        }
        return requests.get(url, headers=headers, verify=False)

    def assign_presentation_request(self, user_id: str, presentation_id: str) -> requests.Response:
        url = f"{self.url}/v1/tenants/{self.tenant}/internal/proofs/proof/{presentation_id}/assign/{user_id}"
        headers = {
            "Content-Type": "application/json"
        }
        return requests.put(url, headers=headers, verify=False)

    def save_presentation(self, presentation_id: str, presentation_data: ProofModel) -> requests.Response:
        url = f"{self.url}/v1/tenants/{self.tenant}/internal/proofs/proof/{presentation_id}"
        headers = {
            "Content-Type": "application/json"
        }
        return requests.post(url, headers=headers, verify=False, data=json.dumps(asdict(presentation_data)))

    def authorize_presentation(self, request_url, user_id: str, ttl: int) -> requests.Response:
        headers = {
            "Content-Type": "application/json",
            "x-ttl": str(ttl),
            "x-tenantId": self.tenant,
            "x-groupId": "",
            "x-did": "did:web:localhost%3A:8080#signerkey",
            # "x-did": "did:jwk:eyJjcnYiOiJQLTI1NiIsImtpZCI6InNpZ25lcmtleSIsImt0eSI6IkVDIiwieCI6IlM3SU5aTXFvUnlySVR0eDM3b043MUxmU245cUxJTlZrdElkZnhTaHZuMW8iLCJ5IjoiSVVDVjY5LUxIRXJXM2loaGVnN05mNTRaNlk4THJmR21DLTBGdjlIeHhCOCJ9",
            "x-key": "signerkey"
        }
        return requests.get(request_url, headers=headers, verify=False, allow_redirects=False)

    def get_authorize_request_url(self, search: str, authUrl: str) -> str:
        pd = Presentation.get_presentation_definition(search)
        pdBytes = json.dumps(pd).encode('utf-8')
        pdEncoded = base64.urlsafe_b64encode(pdBytes).decode('utf-8')

        id, requestId = str(uuid.uuid4()), str(uuid.uuid4())
        ttl = 604800  # 1 week in seconds

        requestUrl = f"{self.url}/v1/tenants/{self.tenant}/presentation/request?tenantId={self.tenant}&id={id}&requestId={requestId}&groupId=&ttl={ttl}&presentationDefinition={pdEncoded}"
        requestUrlEscaped = quote(requestUrl)

        reqUrl = f"{self.url}/v1/tenants/{self.tenant}/presentation/authorize?client_id=mytest&request_uri={requestUrlEscaped}&authUrl={authUrl}"

        return reqUrl

    @staticmethod
    def get_presentation_definition(search: str) -> dict[str, object]:
        field = {
            "path": ["$.credentialSubject"],
            "filter": {
                "pattern": search
            }
        }
        constraints = {
            "limit_disclosure": "",
            "fields": [field]
        }
        inputDescriptor = {
            "description": {
                "id": str(uuid.uuid4()),
                "formatType": "ldp_vc"
            },
            "format": {
                "ldp_vp": {}
            },
            "constraints": constraints,
            "group": []
        }
        result = {
            "id": str(uuid.uuid4()),
            "name": "test",
            "purpose": "I wanna see it!",
            "formatType": "ldp_vp",
            "input_descriptors": [inputDescriptor],
            "format": {
                "ldp_vp": {}
            }
        }
        return result
