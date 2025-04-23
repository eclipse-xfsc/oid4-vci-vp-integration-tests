import json

import requests

from .component import Service


class CredentialRetrieval(Service):

    def __init__(self, url: str, tenant: str):
        super().__init__(url, tenant)

    def offer(self, user_id: str, cred_offer: dict[str, str]) -> requests.Response:
        url = f"{self.url}/v1/tenants/tenant_space/offering/retrieve/{user_id}"
        return requests.put(url, data=json.dumps(cred_offer), verify=False)

    def clear(self, user_id: str, offer_id: str, accepted: bool, user_crypto_key_id: str, user_crypto_key_namespace: str, tx_code: str) -> requests.Response:
        url = f"{self.url}/v1/tenants/tenant_space/offering/clear/{user_id}/{offer_id}"
        acceptance = dict(
            accept=accepted,
            holderKey=user_crypto_key_id,
            holderNamespace=user_crypto_key_namespace,
            holderGroup=user_id,
            tx_code=tx_code
        )
        return requests.delete(url, data=json.dumps(acceptance), verify=False)
